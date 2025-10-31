from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp
from datetime import datetime, timedelta
import os

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'calendar_view.kv')
if os.path.exists(kv_path):
    Builder.load_file(kv_path)


class CalendarDayButton:
    """Простой класс для создания дней календаря с гарантированным отображением цифр"""

    @staticmethod
    def create(day, is_today=False, is_selected=False, is_weekend=False, task_count=0, on_press_callback=None):
        from kivy.uix.button import Button

        # Базовые цвета
        if is_selected:
            bg_color = (0.2, 0.6, 1, 1)  # Синий
            text_color = (1, 1, 1, 1)  # Белый
        elif is_today:
            bg_color = (0.9, 0.95, 1, 1)  # Светло-синий
            text_color = (0.2, 0.6, 1, 1)  # Синий
        elif is_weekend:
            bg_color = (1, 1, 1, 1)  # Белый
            text_color = (0.8, 0.2, 0.2, 1)  # Красный
        else:
            bg_color = (1, 1, 1, 1)  # Белый
            text_color = (0.1, 0.1, 0.1, 1)  # Черный

        # Создаем текст кнопки - просто число
        button_text = str(day)

        # Если есть задачи, добавляем индикатор
        if task_count > 0:
            button_text += "\n•"

        # Создаем кнопку
        day_button = Button(
            text=button_text,
            size_hint_y=None,
            height=dp(60),
            background_color=bg_color,
            background_normal='',
            color=text_color,
            font_size='18sp',
            bold=True,
            halign='center',
            valign='middle'
        )

        # Обработчик нажатия
        if on_press_callback:
            day_button.bind(on_press=lambda instance: on_press_callback(day))

        return day_button


class CalendarScreen(Screen):
    """Упрощенный экран календаря с гарантированным отображением цифр"""

    current_month = StringProperty("")
    current_year = StringProperty("")
    calendar_grid = ObjectProperty(None)
    selected_day = NumericProperty(0)
    selected_date = ObjectProperty(None)
    selected_day_info_text = StringProperty("Выберите день для просмотра задач")

    def __init__(self, task_service=None, **kwargs):
        super().__init__(**kwargs)
        self.task_service = task_service
        self.current_date = datetime.now().replace(day=1)  # Начинаем с первого дня месяца
        self.selected_day = datetime.now().day
        self.selected_date = datetime.now()
        self.tasks_for_selected_day = []
        Clock.schedule_once(self._update_calendar, 0.1)

    def on_enter(self, *args):
        """Вызывается при входе на экран"""
        print("CalendarScreen: Вход на экран")
        self._update_calendar()

    def _go_to_main(self):
        self.manager.current = 'main'

    def _update_calendar(self, dt=None):
        """Обновляет отображение календаря."""
        if not self.calendar_grid:
            print("CalendarScreen: calendar_grid не найден")
            return

        self.calendar_grid.clear_widgets()

        # Устанавливаем заголовок месяца и года
        self.current_month = self._get_month_name(self.current_date.month)
        self.current_year = str(self.current_date.year)

        # Получаем первый день месяца и количество дней
        first_day = self.current_date.replace(day=1)
        days_in_month = self._get_days_in_month(self.current_date.year, self.current_date.month)

        # Добавляем пустые ячейки до первого дня месяца
        first_weekday = first_day.weekday()  # 0-6, где 0 - понедельник
        for _ in range(first_weekday):
            from kivy.uix.widget import Widget
            self.calendar_grid.add_widget(Widget(size_hint_y=None, height=dp(60)))

        # Добавляем дни месяца
        today = datetime.now()
        for day in range(1, days_in_month + 1):
            is_today = (day == today.day and
                        self.current_date.month == today.month and
                        self.current_date.year == today.year)
            is_selected = (day == self.selected_day and
                           self.current_date.month == today.month and
                           self.current_date.year == today.year)
            is_weekend = (first_weekday + day - 1) % 7 >= 5  # Суббота и воскресенье

            # Получаем задачи для этого дня
            day_date = datetime(self.current_date.year, self.current_date.month, day)
            day_tasks = []
            if self.task_service:
                try:
                    day_tasks = self.task_service.get_tasks_by_date(day_date)
                except Exception as e:
                    print(f"CalendarScreen: Ошибка загрузки задач: {e}")

            day_widget = CalendarDayButton.create(
                day=day,
                is_today=is_today,
                is_selected=is_selected,
                is_weekend=is_weekend,
                task_count=len(day_tasks),
                on_press_callback=self._on_day_selected
            )
            self.calendar_grid.add_widget(day_widget)

        # Обновляем информацию о выбранном дне
        self._update_selected_day_info()

    def _update_selected_day_info(self):
        """Обновляет информацию о задачах выбранного дня"""
        if not self.selected_day:
            self.selected_day_info_text = "Выберите день для просмотра задач"
            return

        # Получаем задачи для выбранного дня
        selected_date = datetime(self.current_date.year, self.current_date.month, self.selected_day)
        self.tasks_for_selected_day = []

        if self.task_service:
            try:
                self.tasks_for_selected_day = self.task_service.get_tasks_by_date(selected_date)
            except Exception as e:
                print(f"CalendarScreen: Ошибка загрузки задач: {e}")

        # Обновляем текст информации
        if self.tasks_for_selected_day:
            task_text = f"Задачи на {self.selected_day} {self.current_month}:\n\n"
            for i, task in enumerate(self.tasks_for_selected_day):
                status_icon = "✓" if task.status.value == "Выполнена" else "○"
                priority_color = self._get_priority_color(task.priority.value)
                task_text += f"{status_icon} [color={priority_color}]●[/color] {task.title}\n"
                if i >= 4:  # Ограничиваем количество отображаемых задач
                    task_text += f"... и еще {len(self.tasks_for_selected_day) - 5} задач"
                    break
            self.selected_day_info_text = task_text
        else:
            self.selected_day_info_text = f"На {self.selected_day} {self.current_month} задачи не запланированы"

    def _get_priority_color(self, priority):
        """Возвращает цвет приоритета в hex"""
        colors = {
            "Высокий": "ff4444",  # Красный
            "Средний": "ffaa00",  # Оранжевый
            "Низкий": "44ff44"  # Зеленый
        }
        return colors.get(priority, "888888")

    def _on_day_selected(self, day):
        """Обрабатывает выбор дня."""
        self.selected_day = day
        self.selected_date = datetime(self.current_date.year, self.current_date.month, day)
        print(f"CalendarScreen: Выбран день {day}")
        self._update_calendar()

    def _get_month_name(self, month_num):
        """Возвращает название месяца по номеру"""
        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ""

    def _get_days_in_month(self, year, month):
        """Возвращает количество дней в месяце"""
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        last_day = next_month - timedelta(days=1)
        return last_day.day

    def _prev_month(self):
        """Переход к предыдущему месяцу."""
        try:
            if self.current_date.month == 1:
                new_year = self.current_date.year - 1
                new_month = 12
            else:
                new_year = self.current_date.year
                new_month = self.current_date.month - 1

            self.current_date = datetime(new_year, new_month, 1)
            self.selected_day = 0
            print(f"CalendarScreen: Переход к {new_month}/{new_year}")
            self._update_calendar()
        except Exception as e:
            print(f"CalendarScreen: Ошибка перехода к предыдущему месяцу: {e}")

    def _next_month(self):
        """Переход к следующему месяцу."""
        try:
            if self.current_date.month == 12:
                new_year = self.current_date.year + 1
                new_month = 1
            else:
                new_year = self.current_date.year
                new_month = self.current_date.month + 1

            self.current_date = datetime(new_year, new_month, 1)
            self.selected_day = 0
            print(f"CalendarScreen: Переход к {new_month}/{new_year}")
            self._update_calendar()
        except Exception as e:
            print(f"CalendarScreen: Ошибка перехода к следующему месяцу: {e}")

    def _go_to_today(self):
        """Переход к текущему дню."""
        today = datetime.now()
        self.current_date = today.replace(day=1)
        self.selected_day = today.day
        print("CalendarScreen: Переход к сегодняшнему дню")
        self._update_calendar()