import json
import os
from typing import List, Optional
from datetime import datetime
from core.models import Task, TaskStatus, Priority
from core.exceptions import TaskNotFoundException
from utils.config import ensure_data_dir, TASKS_FILE


class TaskRepository:
    def __init__(self, storage_file=TASKS_FILE):
        ensure_data_dir()
        self.storage_file = storage_file
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Создает файл хранилища если он не существует"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_tasks(self) -> List[dict]:
        """Загружает задачи из JSON файла"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_tasks(self, tasks_data: List[dict]):
        """Сохраняет задачи в JSON файл"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, default=str, ensure_ascii=False)

    def _task_to_dict(self, task: Task) -> dict:
        """Конвертирует Task в словарь"""
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'status': task.status.value,
            'due_date': task.due_date.isoformat(),
            'created_date': task.created_date.isoformat(),
            'completed_date': task.completed_date.isoformat() if task.completed_date else None,
            'reminder_time': task.reminder_time.isoformat() if task.reminder_time else None
        }

    def _dict_to_task(self, data: dict) -> Task:
        """Конвертирует словарь в Task"""
        # Импортируем здесь чтобы избежать циклических импортов
        from core.models import Task, Priority, TaskStatus

        # Обрабатываем даты
        due_date = datetime.fromisoformat(data['due_date'])
        created_date = datetime.fromisoformat(data['created_date'])
        completed_date = datetime.fromisoformat(data['completed_date']) if data['completed_date'] else None
        reminder_time = datetime.fromisoformat(data['reminder_time']) if data['reminder_time'] else None

        # Создаем объект Priority и TaskStatus из строк
        priority = Priority(data['priority'])
        status = TaskStatus(data['status'])

        return Task(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            priority=priority,
            status=status,
            due_date=due_date,
            created_date=created_date,
            completed_date=completed_date,
            reminder_time=reminder_time
        )

    def add_task(self, task: Task):
        """Добавляет новую задачу"""
        tasks_data = self._load_tasks()
        tasks_data.append(self._task_to_dict(task))
        self._save_tasks(tasks_data)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Получает задачу по ID"""
        tasks_data = self._load_tasks()
        for task_data in tasks_data:
            if task_data['id'] == task_id:
                return self._dict_to_task(task_data)
        return None

    def get_all_tasks(self) -> List[Task]:
        """Получает все задачи"""
        tasks_data = self._load_tasks()
        return [self._dict_to_task(task_data) for task_data in tasks_data]

    def update_task(self, task: Task):
        """Обновляет задачу"""
        tasks_data = self._load_tasks()
        task_found = False

        for i, task_data in enumerate(tasks_data):
            if task_data['id'] == task.id:
                tasks_data[i] = self._task_to_dict(task)
                task_found = True
                break

        if not task_found:
            raise TaskNotFoundException(f"Task with id {task.id} not found")

        self._save_tasks(tasks_data)

    def delete_task(self, task_id: str):
        """Удаляет задачу по ID"""
        tasks_data = self._load_tasks()
        initial_length = len(tasks_data)
        tasks_data = [task for task in tasks_data if task['id'] != task_id]

        if len(tasks_data) == initial_length:
            raise TaskNotFoundException(f"Task with id {task_id} not found")

        self._save_tasks(tasks_data)

    def get_tasks_by_date(self, date: datetime) -> List[Task]:
        """Получает задачи на определенную дату"""
        all_tasks = self.get_all_tasks()
        target_date = date.date()
        return [task for task in all_tasks if task.due_date.date() == target_date]

    def get_completed_tasks(self) -> List[Task]:
        """Получает все выполненные задачи"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.status == TaskStatus.COMPLETED]

    def get_pending_tasks(self) -> List[Task]:
        """Получает все невыполненные задачи"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.status != TaskStatus.COMPLETED]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Получает задачи по приоритету"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.priority == priority]