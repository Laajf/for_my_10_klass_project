from enum import Enum
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


class Priority(Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


class TaskStatus(Enum):
    PENDING = "Ожидает"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Выполнена"
    CANCELLED = "Отменена"


@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    status: TaskStatus
    due_date: datetime
    created_date: datetime
    completed_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None

    def __post_init__(self):
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)


@dataclass
class Reminder:
    id: str
    task_id: str
    reminder_time: datetime
    is_sent: bool = False


@dataclass
class DailyStatistics:
    date: datetime
    total_tasks: int
    completed_tasks: int
    productivity_percent: float

    @property
    def completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100