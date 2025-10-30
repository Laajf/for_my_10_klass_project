from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty
from datetime import datetime, timedelta
import os

kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'statistics_screen.kv')
Builder.load_file(kv_path)


class StatisticsScreen(Screen):
    """Экран статистики продуктивности."""

    completed_tasks = NumericProperty(0)
    productivity_percent = NumericProperty(0)
    chart_data = ListProperty([])

    def __init__(self, task_service=None, **kwargs):
        super().__init__(**kwargs)
        self.task_service = task_service

    def on_enter(self, *args):
        """Обновляет статистику при входе на экран"""
        self._update_statistics()

    def _update_statistics(self):
        """Обновляет статистические данные"""
        if not self.task_service:
            return

        try:
            # Получаем все задачи
            all_tasks = self.task_service.get_all_tasks()

            # Считаем выполненные задачи
            completed_tasks = [task for task in all_tasks if task.status.value == "Выполнена"]
            self.completed_tasks = len(completed_tasks)

            # Считаем продуктивность (процент выполненных от всех задач)
            total_tasks = len(all_tasks)
            if total_tasks > 0:
                self.productivity_percent = int((self.completed_tasks / total_tasks) * 100)
            else:
                self.productivity_percent = 0

        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    def _go_to_main(self):
        self.manager.current = 'main'