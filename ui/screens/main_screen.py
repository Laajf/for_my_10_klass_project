from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
import os


# Загружаем KV-файл прямо при импорте
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'main_screen.kv')
Builder.load_file(kv_path)


class MainScreen(Screen):
    """Главный экран — отображает задачи и кнопки навигации."""

    tasks_container = ObjectProperty(None)

    def _go_to_task_editor(self, instance=None):
        self.manager.current = 'task_editor'

    def _go_to_calendar(self, instance=None):
        self.manager.current = 'calendar'

    def _go_to_statistics(self, instance=None):
        self.manager.current = 'statistics'
