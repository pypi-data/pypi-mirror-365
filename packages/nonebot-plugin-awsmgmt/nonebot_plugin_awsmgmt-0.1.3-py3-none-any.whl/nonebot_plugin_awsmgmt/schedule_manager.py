import json
import os
from datetime import datetime, time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class ScheduleState(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"  # 用户手动关闭后暂停

@dataclass
class EC2Schedule:
    instance_id: str
    target_type: str  # "tag" or "id"
    target_key: Optional[str]  # tag key, None for id
    target_value: str  # tag value or instance id
    start_time: str  # "HH:MM" format
    stop_time: str  # "HH:MM" format
    state: str = ScheduleState.ACTIVE.value
    last_manual_action: Optional[str] = None  # "stop", "start", "reboot"
    last_manual_time: Optional[str] = None  # ISO format timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EC2Schedule':
        return cls(**data)

class ScheduleManager:
    def __init__(self, data_dir: str = "."):
        self.data_file = Path(data_dir) / "ec2_schedules.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """确保数据文件存在"""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_schedules({})
    
    def _load_schedules(self) -> Dict[str, Dict[str, Any]]:
        """从文件加载调度数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_schedules(self, schedules: Dict[str, Dict[str, Any]]):
        """保存调度数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
    
    def add_schedule(self, schedule: EC2Schedule) -> bool:
        """添加新的调度"""
        schedules = self._load_schedules()
        schedules[schedule.instance_id] = schedule.to_dict()
        self._save_schedules(schedules)
        return True
    
    def get_schedule(self, instance_id: str) -> Optional[EC2Schedule]:
        """获取指定实例的调度"""
        schedules = self._load_schedules()
        if instance_id in schedules:
            return EC2Schedule.from_dict(schedules[instance_id])
        return None
    
    def get_all_schedules(self) -> List[EC2Schedule]:
        """获取所有调度"""
        schedules = self._load_schedules()
        return [EC2Schedule.from_dict(data) for data in schedules.values()]
    
    def remove_schedule(self, instance_id: str) -> bool:
        """删除调度"""
        schedules = self._load_schedules()
        if instance_id in schedules:
            del schedules[instance_id]
            self._save_schedules(schedules)
            return True
        return False
    
    def update_schedule_state(self, instance_id: str, state: ScheduleState, 
                            manual_action: Optional[str] = None) -> bool:
        """更新调度状态"""
        schedules = self._load_schedules()
        if instance_id in schedules:
            schedules[instance_id]['state'] = state.value
            if manual_action:
                schedules[instance_id]['last_manual_action'] = manual_action
                schedules[instance_id]['last_manual_time'] = datetime.now().isoformat()
            self._save_schedules(schedules)
            return True
        return False
    
    def get_active_schedules(self) -> List[EC2Schedule]:
        """获取所有活跃的调度"""
        return [s for s in self.get_all_schedules() if s.state == ScheduleState.ACTIVE.value]
    
    def should_auto_start(self, schedule: EC2Schedule, current_instance_state: str) -> bool:
        """判断是否应该自动启动实例"""
        # 如果调度被暂停，不启动
        if schedule.state != ScheduleState.ACTIVE.value:
            return False
        
        # 如果实例已经在运行，不需要启动
        if current_instance_state in ['running', 'pending']:
            return False
        
        # 如果用户最近手动停止了实例，不自动启动
        if (schedule.last_manual_action == "stop" and 
            schedule.last_manual_time):
            last_manual = datetime.fromisoformat(schedule.last_manual_time)
            # 检查是否在同一天内手动停止
            if last_manual.date() == datetime.now().date():
                return False
        
        return True
    
    def should_auto_stop(self, schedule: EC2Schedule, current_instance_state: str) -> bool:
        """判断是否应该自动停止实例"""
        # 如果调度被暂停，不停止
        if schedule.state != ScheduleState.ACTIVE.value:
            return False
        
        # 如果实例已经停止，不需要停止
        if current_instance_state in ['stopped', 'stopping']:
            return False
        
        return True
    
    def resume_schedule_if_needed(self, instance_id: str, action: str):
        """在用户手动重启后恢复调度（如果需要）"""
        schedule = self.get_schedule(instance_id)
        if schedule and schedule.state == ScheduleState.SUSPENDED.value:
            if action == "reboot":
                # 用户手动重启后恢复调度
                self.update_schedule_state(instance_id, ScheduleState.ACTIVE, action)
            elif action == "start":
                # 用户手动启动后也恢复调度
                self.update_schedule_state(instance_id, ScheduleState.ACTIVE, action)
    
    def suspend_schedule_if_needed(self, instance_id: str, action: str):
        """在用户手动停止后暂停调度（如果需要）"""
        schedule = self.get_schedule(instance_id)
        if schedule and schedule.state == ScheduleState.ACTIVE.value:
            if action == "stop":
                # 用户手动停止后暂停调度
                self.update_schedule_state(instance_id, ScheduleState.SUSPENDED, action)
    
    def parse_time_range(self, time_str: str) -> Tuple[int, int]:
        """解析时间字符串 HH:MM 返回 (hour, minute)"""
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time range")
            return hour, minute
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM")