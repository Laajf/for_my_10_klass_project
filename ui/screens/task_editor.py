from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
import os

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'task_editor.kv')
Builder.load_file(kv_path)


class TaskEditorScreen(Screen):
    """Экран создания и редактирования задач."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _go_to_main(self):
        self.manager.current = 'main'

    def _save_task(self):
        # Здесь будет логика сохранения задачи
        print("Сохранение задачи...")
        self._go_to_main()