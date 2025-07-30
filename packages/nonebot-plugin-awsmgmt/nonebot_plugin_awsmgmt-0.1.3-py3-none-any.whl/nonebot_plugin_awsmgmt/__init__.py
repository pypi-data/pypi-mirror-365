import time
import re
from typing import Tuple, List, Optional, Dict, Any
from functools import wraps
from datetime import datetime, timedelta

from nonebot import on_command, require, get_bot
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, get_plugin_config
from nonebot.params import CommandArg
from nonebot.adapters import Message, Bot
from nonebot.log import logger
from nonebot.exception import FinishedException

# 导入 APScheduler
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .ec2_manager import EC2Manager
from .cost_explorer_manager import CostExplorerManager
from .lightsail_manager import LightsailManager
from .schedule_manager import ScheduleManager, EC2Schedule, ScheduleState

__plugin_meta__ = PluginMetadata(
    name="AWS Manager",
    description="Manage AWS EC2, Lightsail, and Cost Explorer via commands.",
    usage=(
        "--- EC2 ---\n"
        "/ec2_start|stop|reboot|status [target]\n"
        "Target: tag:Key:Value | id:i-xxxx\n"
        "--- EC2 Schedule ---\n"
        "/ec2_schedule_set <target> <start_time> <stop_time>\n"
        "/ec2_schedule_list\n"
        "/ec2_schedule_remove <target>\n"
        "Time format: HH:MM (24-hour)\n"
        "--- Lightsail ---\n"
        "/lightsail_list\n"
        "/lightsail_start|stop <instance_name>\n"
        "--- Cost ---\n"
        "/aws_cost today|month|month by_service"
    ),
    type="application",
    homepage="https://github.com/maxesisn/nonebot-plugin-awsmgmt",
    config=Config,
    supported_adapters=None
)

def handle_non_finish_exceptions(error_message: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except FinishedException:
                raise
            except Exception as e:
                matcher = args[0] if args else None
                logger.error(f"Error in {func.__name__}: {e}")
                if matcher:
                    await matcher.finish(error_message)
        return wrapper
    return decorator

# --- Init --- #
plugin_config = get_plugin_config(Config)
ec2_manager = EC2Manager(plugin_config)
cost_manager = CostExplorerManager(plugin_config)
lightsail_manager = LightsailManager(plugin_config)
schedule_manager = ScheduleManager()

# --- Command Matchers --- #
# EC2
ec2_start_matcher = on_command("ec2_start", aliases={"ec2启动"}, permission=SUPERUSER)
ec2_stop_matcher = on_command("ec2_stop", aliases={"ec2停止"}, permission=SUPERUSER)
ec2_reboot_matcher = on_command("ec2_reboot", aliases={"ec2重启"}, permission=SUPERUSER)
ec2_status_matcher = on_command("ec2_status", aliases={"ec2状态"}, permission=SUPERUSER)
# EC2 Schedule
ec2_schedule_set_matcher = on_command("ec2_schedule_set", aliases={"ec2定时设置"}, permission=SUPERUSER)
ec2_schedule_list_matcher = on_command("ec2_schedule_list", aliases={"ec2定时列表"}, permission=SUPERUSER)
ec2_schedule_remove_matcher = on_command("ec2_schedule_remove", aliases={"ec2定时删除"}, permission=SUPERUSER)
# Lightsail
lightsail_list_matcher = on_command("lightsail_list", permission=SUPERUSER)
lightsail_start_matcher = on_command("lightsail_start", permission=SUPERUSER)
lightsail_stop_matcher = on_command("lightsail_stop", permission=SUPERUSER)
# Cost Explorer
cost_matcher = on_command("aws_cost", permission=SUPERUSER)


# --- Helper Functions --- #

async def parse_ec2_target(matcher: Matcher, args: Message) -> Tuple[str, str, Optional[str]]:
    arg_str = args.extract_plain_text().strip()
    if not arg_str:
        if plugin_config.aws_default_target_tag:
            arg_str = f"tag:{plugin_config.aws_default_target_tag}"
        else:
            await matcher.finish(__plugin_meta__.usage)
    match = re.match(r"^(tag|id):(.*)$", arg_str)
    if not match:
        await matcher.finish(f"Invalid EC2 target format. \n{__plugin_meta__.usage}")
    target_type, value = match.groups()
    if target_type == "tag":
        if ":" not in value:
            await matcher.finish(f"Invalid tag format. Expected Key:Value. \n{__plugin_meta__.usage}")
        tag_key, tag_value = value.split(":", 1)
        return "tag", tag_key, tag_value
    elif target_type == "id":
        return "id", value, None
    return "unknown", "", None

def format_ec2_status(instance: Dict[str, Any]) -> str:
    instance_id = instance.get('InstanceId', 'N/A')
    state = instance.get('State', {}).get('Name', 'N/A')
    public_ip = instance.get('PublicIpAddress', 'None')
    name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'No Name Tag')
    return f"- {instance_id} ({name_tag})\n  State: {state}\n  Public IP: {public_ip}"


# --- EC2 Handlers --- #

async def ec2_operation(matcher: Matcher, args: Message, operation: str):
    """Helper function to handle EC2 start, stop, and reboot operations."""
    target_type, value1, value2 = await parse_ec2_target(matcher, args)

    states_map = {
        "start": (["stopped"], "running", "start_instances", "instance_running"),
        "stop": (["running"], "stopped", "stop_instances", "instance_stopped"),
        "reboot": (["running"], "running", "reboot_instances", None), # Reboot does not have a waiter
    }

    if operation not in states_map:
        await matcher.finish("Invalid operation.")

    states, target_status, op_func_name, waiter_name = states_map[operation]

    if target_type == "tag":
        instances = await ec2_manager.get_instances_by_tag(value1, value2, states=states)
    else:
        instances = await ec2_manager.get_instances_by_id([value1], states=states)

    if not instances:
        await matcher.finish(f"No instances to {operation}.")

    instance_ids = [inst['InstanceId'] for inst in instances]
    await matcher.send(f"Sending {operation} command to instances:\n" + "\n".join(instance_ids))

    op_func = getattr(ec2_manager, op_func_name)
    await op_func(instance_ids)

    # 更新调度状态
    for instance_id in instance_ids:
        if operation == "stop":
            schedule_manager.suspend_schedule_if_needed(instance_id, operation)
        elif operation in ["start", "reboot"]:
            schedule_manager.resume_schedule_if_needed(instance_id, operation)

    if waiter_name:
        start_time = time.time()
        async with ec2_manager.session.client("ec2") as ec2:
            waiter = ec2.get_waiter(waiter_name)
            await waiter.wait(InstanceIds=instance_ids)
        elapsed_time = time.time() - start_time
        await matcher.finish(f"Successfully {operation}ed instances in {elapsed_time:.2f} seconds.")
    else: # For reboot
        await matcher.finish(f"Successfully sent reboot command to instances.")


@ec2_start_matcher.handle()
@handle_non_finish_exceptions("An error occurred while starting EC2 instances.")
async def handle_ec2_start(matcher: Matcher, args: Message = CommandArg()):
    await ec2_operation(matcher, args, "start")

@ec2_stop_matcher.handle()
@handle_non_finish_exceptions("An error occurred while stopping EC2 instances.")
async def handle_ec2_stop(matcher: Matcher, args: Message = CommandArg()):
    await ec2_operation(matcher, args, "stop")

@ec2_reboot_matcher.handle()
@handle_non_finish_exceptions("An error occurred while rebooting EC2 instances.")
async def handle_ec2_reboot(matcher: Matcher, args: Message = CommandArg()):
    await ec2_operation(matcher, args, "reboot")

@ec2_status_matcher.handle()
@handle_non_finish_exceptions("An error occurred while fetching EC2 status.")
async def handle_ec2_status(matcher: Matcher, args: Message = CommandArg()):
    target_type, value1, value2 = await parse_ec2_target(matcher, args)

    if target_type == "tag":
        instances = await ec2_manager.get_instances_by_tag(value1, value2, states=['pending', 'running', 'stopping', 'stopped'])
    else:
        instances = await ec2_manager.get_instances_by_id([value1], states=['pending', 'running', 'stopping', 'stopped'])
    if not instances:
        await matcher.finish("No EC2 instances found for the specified target.")
    status_list = [format_ec2_status(inst) for inst in instances]
    await matcher.finish("EC2 Instance Status:\n" + "\n".join(status_list))


# ... (omitting other EC2 handlers for brevity, they remain the same)


# --- Lightsail Handlers ---


@lightsail_list_matcher.handle()
@handle_non_finish_exceptions("An error occurred listing Lightsail instances.")
async def handle_lightsail_list(matcher: Matcher):
    instances = await lightsail_manager.get_all_instances()
    if not instances:
        await matcher.finish("No Lightsail instances found.")
    
    def format_lightsail(inst): 
        return f"- {inst['name']} ({inst['state']['name']})\n  Region: {inst['location']['regionName']}\n  IP: {inst['publicIpAddress']}"

    status_list = [format_lightsail(inst) for inst in instances]
    await matcher.finish("Lightsail Instances:\n" + "\n".join(status_list))

@lightsail_start_matcher.handle()
@handle_non_finish_exceptions("An error occurred while starting the Lightsail instance.")
async def handle_lightsail_start(matcher: Matcher, args: Message = CommandArg()):
    instance_name = args.extract_plain_text().strip()
    if not instance_name:
        await matcher.finish("Please provide a Lightsail instance name.")
    
    await matcher.send(f"Sending start command to {instance_name}...\nWaiting for it to become running...")
    await lightsail_manager.start_instance(instance_name)
    await lightsail_manager.wait_for_status(instance_name, 'running')
    await matcher.finish(f"Successfully started Lightsail instance: {instance_name}")

@lightsail_stop_matcher.handle()
@handle_non_finish_exceptions("An error occurred while stopping the Lightsail instance.")
async def handle_lightsail_stop(matcher: Matcher, args: Message = CommandArg()):
    instance_name = args.extract_plain_text().strip()
    if not instance_name:
        await matcher.finish("Please provide a Lightsail instance name.")
    
    await matcher.send(f"Sending stop command to {instance_name}...\nWaiting for it to become stopped...")
    await lightsail_manager.stop_instance(instance_name)
    await lightsail_manager.wait_for_status(instance_name, 'stopped')
    await matcher.finish(f"Successfully stopped Lightsail instance: {instance_name}")


# --- Cost Explorer Handlers ---

@cost_matcher.handle()
@handle_non_finish_exceptions("An error occurred while fetching AWS cost data.")
async def handle_cost(matcher: Matcher, args: Message = CommandArg()):
    sub_command = args.extract_plain_text().strip()
    
    if sub_command == "today":
        result = await cost_manager.get_cost_today()
        cost = result['ResultsByTime'][0]['Total']['UnblendedCost']
        await matcher.finish(f"AWS cost for today: {float(cost['Amount']):.4f} {cost['Unit']}")
    elif sub_command == "month":
        result = await cost_manager.get_cost_this_month()
        cost = result['ResultsByTime'][0]['Total']['UnblendedCost']
        await matcher.finish(f"AWS cost this month: {float(cost['Amount']):.4f} {cost['Unit']}")
    elif sub_command == "month by_service":
        result = await cost_manager.get_cost_this_month_by_service()
        lines = ["Cost this month by service:"]
        for group in sorted(result['ResultsByTime'][0]['Groups'], key=lambda x: float(x['Metrics']['UnblendedCost']['Amount']), reverse=True):
            service_name = group['Keys'][0]
            cost = group['Metrics']['UnblendedCost']
            if float(cost['Amount']) > 0:
                lines.append(f"- {service_name}: {float(cost['Amount']):.4f} {cost['Unit']}")
        await matcher.finish("\n".join(lines))
    else:
        await matcher.finish("Invalid cost command. Use: today, month, month by_service")


# --- EC2 Schedule Handlers ---

async def parse_schedule_target(matcher: Matcher, args: Message) -> Tuple[str, str, Optional[str]]:
    """解析调度目标参数"""
    return await parse_ec2_target(matcher, args)

async def get_instance_id_from_target(target_type: str, value1: str, value2: Optional[str]) -> Optional[str]:
    """从目标参数获取实例ID"""
    if target_type == "tag":
        instances = await ec2_manager.get_instances_by_tag(value1, value2, states=['pending', 'running', 'stopping', 'stopped'])
        if instances:
            return instances[0]['InstanceId']  # 取第一个匹配的实例
    else:
        instances = await ec2_manager.get_instances_by_id([value1], states=['pending', 'running', 'stopping', 'stopped'])
        if instances:
            return instances[0]['InstanceId']
    return None

@ec2_schedule_set_matcher.handle()
@handle_non_finish_exceptions("An error occurred while setting EC2 schedule.")
async def handle_ec2_schedule_set(matcher: Matcher, args: Message = CommandArg()):
    arg_str = args.extract_plain_text().strip()
    parts = arg_str.split()
    
    if len(parts) != 3:
        await matcher.finish("Usage: /ec2_schedule_set <target> <start_time> <stop_time>\nExample: /ec2_schedule_set tag:Name:MyServer 08:00 22:00")
    
    target_str, start_time, stop_time = parts
    
    # 解析目标
    try:
        target_type, value1, value2 = "", "", None
        match = re.match(r"^(tag|id):(.*)$", target_str)
        if not match:
            await matcher.finish("Invalid target format. Use tag:Key:Value or id:i-xxxx")
        target_type, value = match.groups()
        if target_type == "tag":
            if ":" not in value:
                await matcher.finish("Invalid tag format. Expected Key:Value")
            value1, value2 = value.split(":", 1)
        else:
            value1 = value
    except Exception:
        await matcher.finish("Invalid target format. Use tag:Key:Value or id:i-xxxx")
    
    # 验证时间格式
    try:
        schedule_manager.parse_time_range(start_time)
        schedule_manager.parse_time_range(stop_time)
    except ValueError as e:
        await matcher.finish(f"Invalid time format: {e}")
    
    # 获取实例ID
    instance_id = await get_instance_id_from_target(target_type, value1, value2)
    if not instance_id:
        await matcher.finish("No EC2 instances found for the specified target.")
    
    # 创建调度
    schedule = EC2Schedule(
        instance_id=instance_id,
        target_type=target_type,
        target_key=value1,
        target_value=value2 if value2 else value1,
        start_time=start_time,
        stop_time=stop_time
    )
    
    # 添加到调度管理器
    schedule_manager.add_schedule(schedule)
    
    # 添加定时任务
    setup_schedule_jobs(schedule)
    
    await matcher.finish(f"Successfully set schedule for instance {instance_id}:\nStart: {start_time}, Stop: {stop_time}")

@ec2_schedule_list_matcher.handle()
@handle_non_finish_exceptions("An error occurred while listing EC2 schedules.")
async def handle_ec2_schedule_list(matcher: Matcher):
    schedules = schedule_manager.get_all_schedules()
    if not schedules:
        await matcher.finish("No EC2 schedules found.")
    
    lines = ["EC2 Schedules:"]
    for schedule in schedules:
        status = "🟢 Active" if schedule.state == ScheduleState.ACTIVE.value else "🔴 Suspended"
        target_info = f"{schedule.target_key}:{schedule.target_value}" if schedule.target_type == "tag" else schedule.target_value
        lines.append(f"- {schedule.instance_id} ({target_info})")
        lines.append(f"  Start: {schedule.start_time}, Stop: {schedule.stop_time}")
        lines.append(f"  Status: {status}")
        if schedule.last_manual_action and schedule.last_manual_time:
            last_time = datetime.fromisoformat(schedule.last_manual_time).strftime("%Y-%m-%d %H:%M")
            lines.append(f"  Last manual action: {schedule.last_manual_action} at {last_time}")
        lines.append("")
    
    await matcher.finish("\n".join(lines))

@ec2_schedule_remove_matcher.handle()
@handle_non_finish_exceptions("An error occurred while removing EC2 schedule.")
async def handle_ec2_schedule_remove(matcher: Matcher, args: Message = CommandArg()):
    target_type, value1, value2 = await parse_schedule_target(matcher, args)
    
    # 获取实例ID
    instance_id = await get_instance_id_from_target(target_type, value1, value2)
    if not instance_id:
        await matcher.finish("No EC2 instances found for the specified target.")
    
    # 检查调度是否存在
    schedule = schedule_manager.get_schedule(instance_id)
    if not schedule:
        await matcher.finish(f"No schedule found for instance {instance_id}.")
    
    # 删除调度
    if schedule_manager.remove_schedule(instance_id):
        # 移除定时任务
        remove_schedule_jobs(instance_id)
        await matcher.finish(f"Successfully removed schedule for instance {instance_id}.")
    else:
        await matcher.finish(f"Failed to remove schedule for instance {instance_id}.")


# --- Scheduled Job Functions ---

def setup_schedule_jobs(schedule: EC2Schedule):
    """设置单个实例的定时任务"""
    instance_id = schedule.instance_id
    
    # 移除旧任务（如果存在）
    remove_schedule_jobs(instance_id)
    
    # 解析时间
    start_hour, start_minute = schedule_manager.parse_time_range(schedule.start_time)
    stop_hour, stop_minute = schedule_manager.parse_time_range(schedule.stop_time)
    
    # 添加启动任务
    scheduler.add_job(
        auto_start_instance,
        "cron",
        hour=start_hour,
        minute=start_minute,
        id=f"start_{instance_id}",
        args=[instance_id],
        replace_existing=True
    )
    
    # 添加停止任务
    scheduler.add_job(
        auto_stop_instance,
        "cron",
        hour=stop_hour,
        minute=stop_minute,
        id=f"stop_{instance_id}",
        args=[instance_id],
        replace_existing=True
    )

def remove_schedule_jobs(instance_id: str):
    """移除实例的所有定时任务"""
    job_ids = [
        f"start_{instance_id}",
        f"stop_{instance_id}",
        f"notify_start_{instance_id}",
        f"notify_stop_{instance_id}"
    ]
    
    for job_id in job_ids:
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass  # 任务可能不存在

async def auto_start_instance(instance_id: str):
    """自动启动实例"""
    try:
        schedule = schedule_manager.get_schedule(instance_id)
        if not schedule:
            logger.warning(f"No schedule found for instance {instance_id}")
            return
        
        # 获取当前实例状态
        instances = await ec2_manager.get_instances_by_id([instance_id], states=['pending', 'running', 'stopping', 'stopped'])
        if not instances:
            logger.warning(f"Instance {instance_id} not found")
            return
        
        current_state = instances[0]['State']['Name']
        
        # 检查是否应该启动
        if schedule_manager.should_auto_start(schedule, current_state):
            await ec2_manager.start_instances([instance_id])
            logger.info(f"Auto-started instance {instance_id}")
        else:
            logger.info(f"Skipped auto-start for instance {instance_id} (state: {current_state}, schedule state: {schedule.state})")
            
    except Exception as e:
        logger.error(f"Error in auto_start_instance for {instance_id}: {e}")

async def auto_stop_instance(instance_id: str):
    """自动停止实例"""
    try:
        schedule = schedule_manager.get_schedule(instance_id)
        if not schedule:
            logger.warning(f"No schedule found for instance {instance_id}")
            return
        
        # 获取当前实例状态
        instances = await ec2_manager.get_instances_by_id([instance_id], states=['pending', 'running', 'stopping', 'stopped'])
        if not instances:
            logger.warning(f"Instance {instance_id} not found")
            return
        
        current_state = instances[0]['State']['Name']
        
        # 检查是否应该停止
        if schedule_manager.should_auto_stop(schedule, current_state):
            await ec2_manager.stop_instances([instance_id])
            logger.info(f"Auto-stopped instance {instance_id}")
        else:
            logger.info(f"Skipped auto-stop for instance {instance_id} (state: {current_state}, schedule state: {schedule.state})")
            
    except Exception as e:
        logger.error(f"Error in auto_stop_instance for {instance_id}: {e}")

# 初始化时加载所有现有的调度任务
def init_existing_schedules():
    """初始化现有的调度任务"""
    try:
        schedules = schedule_manager.get_active_schedules()
        for schedule in schedules:
            setup_schedule_jobs(schedule)
        logger.info(f"Initialized {len(schedules)} existing schedules")
    except Exception as e:
        logger.error(f"Error initializing existing schedules: {e}")

# 插件加载时初始化调度
init_existing_schedules()
