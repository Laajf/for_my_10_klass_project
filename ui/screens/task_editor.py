from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
import os

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'task_editor.kv')
Builder.load_file(kv_path)


class TaskEditorScreen(Screen):
    """Экран создания и редактирования задач."""

    task_title = StringProperty("")
    task_description = StringProperty("")
    task_priority = StringProperty("Средний")  # По умолчанию средний приоритет
    task_date = StringProperty("")
    task_reminder = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _go_to_main(self):
        """Возврат на главный экран."""
        self.manager.current = 'main'

    def on_priority_change(self, button):
        """Обработчик изменения приоритета."""
        if button.state == 'down':
            self.task_priority = button.text
            print(f"Выбран приоритет: {self.task_priority}")

    def _save_task(self):
        """Сохранение задачи."""
        # Получаем данные из полей ввода
        title = self.ids.task_title.text
        description = self.ids.task_description.text

        print(f"Сохранение задачи: {title}")
        print(f"Описание: {description}")
        print(f"Приоритет: {self.task_priority}")

        # Здесь будет логика сохранения задачи в базу данных
        # ...

        self._go_to_main()

    def _select_date(self):
        """Выбор даты для задачи."""
        print("Открытие выбора даты...")
        # Здесь будет логика открытия календаря для выбора даты

    def _set_reminder(self):
        """Установка напоминания."""
        print("Установка напоминания...")
        # Здесь будет логика установки напоминания

    def clear_form(self):
        """Очистка формы при открытии."""
        self.ids.task_title.text = ""
        self.ids.task_description.text = ""
        # Сбрасываем приоритет на средний
        self.ids.medium_priority.state = 'down'
        self.task_priority = "Средний"