import uuid
from datetime import datetime
from typing import List, Optional
from core.models import Task, TaskStatus, Priority
from repository.task_repository import TaskRepository
from services.notification_service import NotificationService
from core.exceptions import InvalidTaskDataException


class TaskService:
    def __init__(self):
        self.task_repository = TaskRepository()
        self.notification_service = NotificationService()
        print("TaskService инициализирован")

    def create_task(self, title: str, description: str, priority: Priority, due_date: datetime,
                    reminder_time: Optional[datetime] = None) -> Task:
        """Создает новую задачу"""
        print(f"Создание задачи: {title}, дата: {due_date}")

        if not title or not title.strip():
            raise InvalidTaskDataException("Title cannot be empty")

        task = Task(
            id=str(uuid.uuid4()),
            title=title.strip(),
            description=description.strip(),
            priority=priority,
            status=TaskStatus.PENDING,
            due_date=due_date,
            created_date=datetime.now(),
            reminder_time=reminder_time
        )

        self.task_repository.add_task(task)
        print(f"Задача сохранена в репозиторий: {task.title}")

        # Планируем напоминание если указано
        if reminder_time:
            self.notification_service.schedule_reminder(task)

        return task

    def get_all_tasks(self) -> List[Task]:
        """Получает все задачи"""
        tasks = self.task_repository.get_all_tasks()
        print(f"Загружено задач из репозитория: {len(tasks)}")
        return tasks

    def get_today_tasks(self) -> List[Task]:
        """Получает задачи на сегодня"""
        today = datetime.now().date()
        all_tasks = self.get_all_tasks()
        today_tasks = [task for task in all_tasks if
                      task.due_date.date() == today and
                      task.status != TaskStatus.COMPLETED]
        print(f"Задачи на сегодня: {len(today_tasks)}")
        for task in today_tasks:
            print(f"  - {task.title} (статус: {task.status.value}, дата: {task.due_date.date()})")
        return today_tasks

    def complete_task(self, task_id: str):
        """Отмечает задачу как выполненную"""
        task = self.task_repository.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_date = datetime.now()
            self.task_repository.update_task(task)

            # Отменяем напоминание для выполненной задачи
            self.notification_service.cancel_reminder(task_id)
            print(f"Задача выполнена: {task.title}")

    def update_task(self, task_id: str, **kwargs):
        """Обновляет задачу"""
        task = self.task_repository.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.task_repository.update_task(task)

    def delete_task(self, task_id: str):
        """Удаляет задачу"""
        self.notification_service.cancel_reminder(task_id)
        self.task_repository.delete_task(task_id)

    def get_tasks_by_date(self, date: datetime) -> List[Task]:
        """Получает задачи на определенную дату"""
        tasks = self.task_repository.get_tasks_by_date(date)
        print(f"Задачи на {date.date()}: {len(tasks)}")
        for task in tasks:
            print(f"  - {task.title} (статус: {task.status.value})")
        return tasks