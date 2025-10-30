from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
import os

# Загружаем KV-файлы
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'main_screen.kv')
Builder.load_file(kv_path)

# Импортируем нашу современную карточку задачи
from ui.widgets.task_card import TaskCard


class MainScreen(Screen):
    """Главный экран в современном стиле"""

    tasks_container = ObjectProperty(None)

    def __init__(self, task_service=None, **kwargs):
        super().__init__(**kwargs)
        self.task_service = task_service
        Clock.schedule_once(self._load_tasks, 0.1)

    def _load_tasks(self, dt=None):
        """Загружает задачи при входе на экран"""
        if self.task_service and self.tasks_container:
            self._update_tasks_display()

    def _update_tasks_display(self):
        """Обновляет отображение задач"""
        if not self.tasks_container:
            return

        self.tasks_container.clear_widgets()

        try:
            today_tasks = self.task_service.get_today_tasks()

            if not today_tasks:
                self._show_empty_state()
                return

            # Добавляем отступ сверху
            from kivy.uix.widget import Widget
            self.tasks_container.add_widget(Widget(size_hint_y=None, height=dp(8)))

            for task in today_tasks:
                task_widget = TaskCard(task, self._complete_task)
                self.tasks_container.add_widget(task_widget)

                # Добавляем маленький разделитель между задачами
                separator = Widget(size_hint_y=None, height=dp(8))
                self.tasks_container.add_widget(separator)

            print(f"MainScreen: Отображено {len(today_tasks)} задач")

        except Exception as e:
            print(f"MainScreen: Ошибка загрузки задач: {e}")
            import traceback
            traceback.print_exc()

    def _show_empty_state(self):
        """Показывает красивое состояние при отсутствии задач"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label

        empty_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            padding=dp(40),
            spacing=dp(16)
        )

        empty_label = Label(
            text="[color=cccccc]✓[/color]\n[b]Все задачи выполнены![/b]\n\nСоздайте новую задачу\nили проверьте календарь",
            font_size='16sp',
            color=(0.6, 0.6, 0.6, 1),
            halign='center',
            valign='middle',
            text_size=(None, None),
            markup=True
        )

        empty_container.add_widget(empty_label)
        self.tasks_container.add_widget(empty_container)
        print("MainScreen: Нет задач на сегодня")

    def _complete_task(self, task_id):
        """Отмечает задачу как выполненную"""
        try:
            self.task_service.complete_task(task_id)
            # Не обновляем сразу - пусть пользователь видит анимацию
            Clock.schedule_once(lambda dt: self._update_tasks_display(), 0.3)
            print(f"Задача {task_id} отмечена как выполненная")
        except Exception as e:
            print(f"Ошибка выполнения задачи: {e}")

    def on_enter(self, *args):
        """Обновляет задачи при входе на экран"""
        Clock.schedule_once(self._load_tasks, 0.1)

    def _go_to_task_editor(self, instance=None):
        self.manager.current = 'task_editor'

    def _go_to_calendar(self, instance=None):
        self.manager.current = 'calendar'

    def _go_to_statistics(self, instance=None):
        self.manager.current = 'statistics'