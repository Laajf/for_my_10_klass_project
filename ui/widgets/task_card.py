from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.metrics import dp
from kivy.lang import Builder
import os

# Загружаем KV-файл для карточки задачи
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'task_card.kv')
if os.path.exists(kv_path):
    Builder.load_file(kv_path)


class TaskCard(BoxLayout):
    """Современная карточка задачи в стиле Todoist/Notion"""

    title = StringProperty("")
    description = StringProperty("")
    date_text = StringProperty("")
    time_text = StringProperty("")
    priority = StringProperty("Средний")
    priority_color = ListProperty([0.5, 0.5, 0.5, 1])
    is_completed = BooleanProperty(False)

    def __init__(self, task, on_complete_callback, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.on_complete_callback = on_complete_callback

        # Устанавливаем свойства
        self.title = task.title
        self.description = task.description if task.description else ""
        self.is_completed = task.status.value == "Выполнена"

        from utils.date_utils import format_date_display, format_time_display
        self.date_text = format_date_display(task.due_date)
        self.time_text = format_time_display(task.due_date)
        self.priority = task.priority.value

        # Устанавливаем цвета в зависимости от приоритета
        self._set_priority_colors()

    def _set_priority_colors(self):
        """Устанавливает цвета в зависимости от приоритета"""
        priority_styles = {
            "Высокий": [0.88, 0.24, 0.19, 1],  # Красный как в Todoist
            "Средний": [1.0, 0.62, 0.11, 1],  # Оранжевый
            "Низкий": [0.16, 0.63, 0.33, 1]  # Зеленый
        }

        self.priority_color = priority_styles.get(self.priority, [0.44, 0.44, 0.44, 1])

    def toggle_completion(self):
        """Переключает состояние выполнения задачи"""
        if not self.is_completed and self.on_complete_callback:
            self.on_complete_callback(self.task.id)