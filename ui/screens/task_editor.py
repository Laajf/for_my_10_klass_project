from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from datetime import datetime, timedelta
from core.models import Priority
import os

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'task_editor.kv')
Builder.load_file(kv_path)


class TaskEditorScreen(Screen):
    """Экран создания и редактирования задач."""

    def __init__(self, task_service=None, **kwargs):
        super().__init__(**kwargs)
        self.task_service = task_service
        # Устанавливаем дату на СЕГОДНЯ по умолчанию, чтобы задача сразу отображалась
        self.selected_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        self.reminder_time = None
        Clock.schedule_once(self._setup_initial_state, 0.1)

    def _setup_initial_state(self, dt):
        """Устанавливает начальное состояние формы"""
        if hasattr(self, 'ids') and 'medium_priority' in self.ids:
            self.ids.medium_priority.state = 'down'
        self._update_date_display()

    def on_enter(self, *args):
        """Очищает форму при каждом входе на экран"""
        self.clear_form()

    def _go_to_main(self):
        """Возврат на главный экран."""
        self.manager.current = 'main'

    def on_priority_change(self, button):
        """Обработчик изменения приоритета."""
        if button.state == 'down':
            print(f"Выбран приоритет: {button.text}")

    def _save_task(self):
        """Сохранение задачи."""
        try:
            # Получаем данные из полей ввода
            title = self.ids.task_title.text.strip()
            description = self.ids.task_description.text.strip()

            # Валидация
            if not title:
                self._show_error("Название задачи не может быть пустым")
                return

            # Определяем выбранный приоритет по состоянию кнопок
            if self.ids.high_priority.state == 'down':
                selected_priority_text = "ВЫСОКИЙ"
                priority = Priority.HIGH
            elif self.ids.medium_priority.state == 'down':
                selected_priority_text = "СРЕДНИЙ"
                priority = Priority.MEDIUM
            elif self.ids.low_priority.state == 'down':
                selected_priority_text = "НИЗКИЙ"
                priority = Priority.LOW
            else:
                selected_priority_text = "СРЕДНИЙ"
                priority = Priority.MEDIUM

            print(f"Сохранение задачи: {title}")
            print(f"Описание: {description}")
            print(f"Приоритет: {selected_priority_text}")
            print(f"Дата: {self.selected_date}")

            # Создаем задачу
            task = self.task_service.create_task(
                title=title,
                description=description,
                priority=priority,
                due_date=self.selected_date,
                reminder_time=self.reminder_time
            )

            print(f"Задача успешно создана: {task.title}")
            print(f"ID задачи: {task.id}")
            print(f"Статус задачи: {task.status.value}")

            # Проверяем, что задача действительно сохранилась
            all_tasks = self.task_service.get_all_tasks()
            print(f"Всего задач в системе: {len(all_tasks)}")
            for t in all_tasks:
                print(f" - {t.title} (ID: {t.id})")

            self._go_to_main()

        except Exception as e:
            print(f"Ошибка сохранения задачи: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"Ошибка: {str(e)}")

    def _show_error(self, message):
        """Показывает сообщение об ошибке"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))

        btn = Button(text='OK', size_hint_y=0.4)
        popup = Popup(title='Ошибка', content=content, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)

        popup.open()

    def _select_date(self):
        """Выбор даты для задачи."""
        print("Открытие выбора даты...")
        # Устанавливаем дату на завтра по умолчанию
        self.selected_date = datetime.now() + timedelta(days=1)
        self._update_date_display()
        self._show_date_selected()

    def _update_date_display(self):
        """Обновляет отображение даты на кнопке"""
        if hasattr(self, 'ids') and 'date_button' in self.ids:
            from utils.date_utils import format_date_display, format_time_display
            date_str = f"{format_date_display(self.selected_date)}, {format_time_display(self.selected_date)}"
            self.ids.date_button.text = date_str

    def _set_reminder(self):
        """Установка напоминания."""
        print("Установка напоминания...")
        # Устанавливаем напоминание за 30 минут до дедлайна
        if self.selected_date:
            self.reminder_time = self.selected_date - timedelta(minutes=30)
            self._show_reminder_set()

    def _show_date_selected(self):
        """Показывает выбранную дату"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Дата установлена: {self.selected_date.strftime('%d.%m.%Y %H:%M')}"
        ))

        btn = Button(text='OK', size_hint_y=0.4)
        popup = Popup(title='Дата установлена', content=content, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)

        popup.open()

    def _show_reminder_set(self):
        """Показывает установленное напоминание"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        reminder_str = self.reminder_time.strftime('%d.%m.%Y %H:%M') if self.reminder_time else "Не установлено"
        content.add_widget(Label(text=f"Напоминание: {reminder_str}"))

        btn = Button(text='OK', size_hint_y=0.4)
        popup = Popup(title='Напоминание установлено', content=content, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)

        popup.open()

    def clear_form(self):
        """Очистка формы при открытии."""
        if hasattr(self, 'ids'):
            self.ids.task_title.text = ""
            self.ids.task_description.text = ""
            # Сбрасываем приоритет на средний
            if 'medium_priority' in self.ids:
                self.ids.medium_priority.state = 'down'

            # Сбрасываем даты
            self.selected_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
            self.reminder_time = None
            self._update_date_display()