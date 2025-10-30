from datetime import datetime
from core.models import Task
from plyer import notification
import threading
import time


class NotificationService:
    def __init__(self):
        self.scheduled_reminders = {}

    def schedule_reminder(self, task: Task):
        """Планирует напоминание для задачи"""
        if not task.reminder_time:
            return

        reminder_id = f"task_{task.id}"

        # Отменяем существующее напоминание
        self.cancel_reminder(task.id)

        # Вычисляем задержку до напоминания
        now = datetime.now()
        delay = (task.reminder_time - now).total_seconds()

        if delay > 0:
            timer = threading.Timer(delay, self._show_notification, [task])
            timer.start()
            self.scheduled_reminders[task.id] = timer

    def _show_notification(self, task: Task):
        """Показывает уведомление"""
        try:
            notification.notify(
                title=f"Напоминание: {task.title}",
                message=f"Срок выполнения: {task.due_date.strftime('%H:%M')}",
                timeout=10
            )
        except Exception as e:
            print(f"Ошибка показа уведомления: {e}")

    def cancel_reminder(self, task_id: str):
        """Отменяет запланированное напоминание"""
        if task_id in self.scheduled_reminders:
            self.scheduled_reminders[task_id].cancel()
            del self.scheduled_reminders[task_id]