from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from datetime import datetime, timedelta
import os
import re
import threading

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp

from utils.ai_utils import estimate_min_duration_and_plan
from core.models import Priority
from utils.date_utils import format_date_display

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'ai_plan_screen.kv')
Builder.load_file(kv_path)


class AIPlanScreen(Screen):
    """Экран AI-планирования: генерация расписания по цели и создание задач."""

    goal = StringProperty("")
    current_level = StringProperty("")
    target_level = StringProperty("")
    minutes_per_day = NumericProperty(30)
    desired_days = StringProperty("")
    result_text = StringProperty("")
    start_date_text = StringProperty("Сегодня")
    can_create = BooleanProperty(False)
    generated_plan = None

    def __init__(self, task_service=None, **kwargs):
        super().__init__(**kwargs)
        self.task_service = task_service
        self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self._loading_modal = None

    def on_enter(self, *args):
        self.goal = ""
        self.current_level = ""
        self.target_level = ""
        self.minutes_per_day = 30
        self.desired_days = ""
        self.result_text = ""
        self.can_create = False
        self.generated_plan = None
        self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.start_date_text = format_date_display(self.start_date)

    def generate_plan(self):
        """Запускает генерацию плана в отдельном потоке, показывает модальное окно."""
        if not self.goal.strip():
            self.result_text = "[color=ff0000]Введите цель[/color]"
            return

        # Парсим желаемый срок, если введён
        days_input = self.desired_days.strip()
        if days_input:
            try:
                deadline = int(days_input)
                if deadline <= 0:
                    raise ValueError
            except ValueError:
                self.result_text = "[color=ff0000]Срок должен быть положительным числом[/color]"
                return

        # Показываем модальное окно загрузки
        self._show_loading_modal()

        # Запускаем AI в фоновом потоке
        thread = threading.Thread(target=self._run_ai_estimation)
        thread.daemon = True
        thread.start()

    def _show_loading_modal(self):
        """Создаёт и показывает модальное окно с сообщением о загрузке."""
        self._loading_modal = ModalView(
            size_hint=(0.6, 0.3),
            background_color=(0, 0, 0, 0.7),
            auto_dismiss=False  # нельзя закрыть случайно
        )
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(
            text="Генерация плана...\nПожалуйста, подождите",
            font_size='18sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        ))
        self._loading_modal.add_widget(content)
        self._loading_modal.open()

    def _close_loading_modal(self):
        """Закрывает модальное окно загрузки, если оно открыто."""
        if self._loading_modal:
            self._loading_modal.dismiss()
            self._loading_modal = None

    def _run_ai_estimation(self):
        """Выполняет вызов AI (в фоновом потоке)."""
        try:
            result = estimate_min_duration_and_plan(
                goal=self.goal,
                current_level=self.current_level,
                target_level=self.target_level,
                minutes_per_day=int(self.minutes_per_day)
            )
            # Возвращаем результат в главный поток
            Clock.schedule_once(lambda dt: self._on_ai_result(result))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_ai_error(str(e)))

    def _on_ai_result(self, result):
        """Обрабатывает успешный результат AI (в главном потоке)."""
        self._close_loading_modal()
        if result == 0:
            self.result_text = "[color=ff0000]Эта цель недостижима даже в теории. Попробуйте изменить параметры.[/color]"
            self.can_create = False
            self.generated_plan = None
        else:
            min_days, schedule = result
            self.generated_plan = (min_days, schedule)
            lines = [f"[b]Минимально потребуется {min_days} дней[/b]\n"]
            lines.extend(schedule)
            self.result_text = "\n".join(lines)
            self.can_create = True

    def _on_ai_error(self, error_msg):
        """Обрабатывает ошибку AI (в главном потоке)."""
        self._close_loading_modal()
        self.result_text = f"[color=ff0000]Ошибка при обращении к AI: {error_msg}[/color]"
        self.can_create = False
        self.generated_plan = None

    def create_tasks(self):
        """Создаёт задачи в календаре на основе сгенерированного плана, начиная с выбранной даты."""
        if not self.can_create or not self.generated_plan:
            return

        min_days, schedule = self.generated_plan
        start_date = self.start_date

        day_pattern = re.compile(r'День\s*(\d+)\s*:\s*(.*)', re.IGNORECASE)

        tasks_created = 0
        for line in schedule:
            match = day_pattern.match(line.strip())
            if match:
                day_num = int(match.group(1))
                action = match.group(2).strip()
                due_date = start_date + timedelta(days=day_num - 1)

                self.task_service.create_task(
                    title=f"{self.goal} – день {day_num}",
                    description=action,
                    priority=Priority.MEDIUM,
                    due_date=due_date,
                    reminder_time=None
                )
                tasks_created += 1

        self.result_text = f"[color=00aa00]Создано {tasks_created} задач![/color]"
        self.can_create = False
        self.generated_plan = None

        # Возврат на главный экран через 2 секунды
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main'), 2)

    def go_back(self):
        """Возврат на экран создания задачи."""
        self.manager.current = 'task_editor'

    def select_start_date(self):
        """Открывает диалог выбора даты начала."""
        modal = ModalView(
            size_hint=(0.85, 0.7),
            background_color=(0, 0, 0, 0.3),
            overlay_color=(0, 0, 0, 0.5)
        )

        main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(0),
            padding=dp(0)
        )

        # Заголовок
        header_layout = BoxLayout(
            size_hint_y=0.15,
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )
        header_label = Label(
            text='Выберите дату начала',
            font_size='20sp',
            bold=True,
            color=(0.1, 0.15, 0.25, 1)
        )
        header_layout.add_widget(header_label)
        main_layout.add_widget(header_layout)

        # Навигация по месяцам
        nav_layout = BoxLayout(
            size_hint_y=0.1,
            padding=[dp(20), dp(5)],
            spacing=dp(10)
        )

        prev_btn = Button(
            text='←',
            font_size='18sp',
            background_color=(0.9, 0.9, 0.9, 1),
            background_normal='',
            color=(0.3, 0.3, 0.3, 1)
        )

        temp_date = self.start_date
        month_label = Label(
            text=self._get_month_name(temp_date.month) + " " + str(temp_date.year),
            font_size='16sp',
            bold=True,
            color=(0.1, 0.15, 0.25, 1)
        )

        next_btn = Button(
            text='→',
            font_size='18sp',
            background_color=(0.9, 0.9, 0.9, 1),
            background_normal='',
            color=(0.3, 0.3, 0.3, 1)
        )

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(month_label)
        nav_layout.add_widget(next_btn)
        main_layout.add_widget(nav_layout)

        # Дни недели
        days_header = GridLayout(
            cols=7,
            size_hint_y=0.08,
            spacing=dp(2)
        )

        days_of_week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        for day in days_of_week:
            day_label = Label(
                text=day,
                font_size='12sp',
                bold=True,
                color=(0.4, 0.4, 0.4, 1)
            )
            days_header.add_widget(day_label)
        main_layout.add_widget(days_header)

        # Сетка календаря
        calendar_grid = GridLayout(
            cols=7,
            spacing=dp(2),
            padding=dp(15),
            size_hint_y=0.67
        )

        def update_grid(*args):
            calendar_grid.clear_widgets()
            first_day = temp_date.replace(day=1)
            days_in_month = self._get_days_in_month(temp_date.year, temp_date.month)
            first_weekday = first_day.weekday()

            for _ in range(first_weekday):
                calendar_grid.add_widget(Widget())

            today = datetime.now().date()
            for day in range(1, days_in_month + 1):
                day_date = datetime(temp_date.year, temp_date.month, day).date()
                is_today = day_date == today
                is_selected = day_date == self.start_date.date()

                if is_selected:
                    btn = Button(
                        text=str(day),
                        background_color=(0.2, 0.6, 1, 1),
                        background_normal='',
                        color=(1, 1, 1, 1),
                        bold=True
                    )
                elif is_today:
                    btn = Button(
                        text=str(day),
                        background_color=(0.9, 0.95, 1, 1),
                        background_normal='',
                        color=(0.2, 0.6, 1, 1),
                        bold=True
                    )
                else:
                    btn = Button(
                        text=str(day),
                        background_color=(1, 1, 1, 1),
                        background_normal='',
                        color=(0.1, 0.1, 0.1, 1)
                    )

                btn.bind(on_press=lambda instance, d=day: self._on_start_date_selected(d, temp_date, modal))
                calendar_grid.add_widget(btn)

        update_grid()

        def change_month(delta):
            nonlocal temp_date
            new_month = temp_date.month + delta
            new_year = temp_date.year
            if new_month > 12:
                new_month = 1
                new_year += 1
            elif new_month < 1:
                new_month = 12
                new_year -= 1
            temp_date = temp_date.replace(year=new_year, month=new_month, day=1)
            month_label.text = self._get_month_name(temp_date.month) + " " + str(temp_date.year)
            update_grid()

        prev_btn.bind(on_press=lambda x: change_month(-1))
        next_btn.bind(on_press=lambda x: change_month(1))

        actions_layout = BoxLayout(
            size_hint_y=0.1,
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )

        today_btn = Button(
            text='Сегодня',
            background_color=(0.9, 0.9, 0.9, 1),
            background_normal='',
            color=(0.3, 0.3, 0.3, 1)
        )

        cancel_btn = Button(
            text='Отмена',
            background_color=(0.9, 0.9, 0.9, 1),
            background_normal='',
            color=(0.3, 0.3, 0.3, 1)
        )

        actions_layout.add_widget(today_btn)
        actions_layout.add_widget(cancel_btn)
        main_layout.add_widget(actions_layout)

        def select_today(instance):
            self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            self.start_date_text = format_date_display(self.start_date)
            modal.dismiss()

        def on_cancel(instance):
            modal.dismiss()

        today_btn.bind(on_press=select_today)
        cancel_btn.bind(on_press=on_cancel)

        modal.add_widget(main_layout)
        modal.open()

    def _on_start_date_selected(self, day, temp_date, modal):
        self.start_date = datetime(temp_date.year, temp_date.month, day)
        self.start_date_text = format_date_display(self.start_date)
        modal.dismiss()

    def _get_month_name(self, month_num):
        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        return months[month_num - 1] if 1 <= month_num <= 12 else ""

    def _get_days_in_month(self, year, month):
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        return last_day.day