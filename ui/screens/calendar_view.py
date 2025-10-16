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


class CalendarScreen(Screen):
    """Современный экран календаря в стиле Google Calendar."""

    current_month = StringProperty("")
    current_year = StringProperty("")
    calendar_grid = ObjectProperty(None)
    selected_day = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = datetime.now()
        self.selected_day = self.current_date.day
        Clock.schedule_once(self._update_calendar, 0.1)

    def on_enter(self, *args):
        """Вызывается при входе на экран"""
        self._update_calendar()

    def _go_to_main(self):
        self.manager.current = 'main'

    def _update_calendar(self, dt=None):
        """Обновляет отображение календаря."""
        if not self.calendar_grid:
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
            self.calendar_grid.add_widget(Widget(size_hint_y=None, height=dp(50)))

        # Добавляем дни месяца
        today = datetime.now()
        for day in range(1, days_in_month + 1):
            is_today = (day == today.day and
                        self.current_date.month == today.month and
                        self.current_date.year == today.year)
            is_selected = (day == self.selected_day)
            is_weekend = (first_weekday + day - 1) % 7 >= 5  # Суббота и воскресенье

            day_widget = self._create_day_widget(day, is_today, is_selected, is_weekend)
            self.calendar_grid.add_widget(day_widget)

    def _create_day_widget(self, day, is_today=False, is_selected=False, is_weekend=False):
        """Создает современный виджет дня в стиле Google Calendar."""
        from kivy.uix.button import Button

        # Базовые стили
        bg_color = (1, 1, 1, 1)  # Белый фон
        text_color = (0.2, 0.2, 0.2, 1)  # Темно-серый текст

        if is_weekend:
            text_color = (0.9, 0.26, 0.21, 1)  # Красный для выходных

        if is_selected:
            bg_color = (0.26, 0.55, 0.96, 1)  # Синий для выбранного дня
            text_color = (1, 1, 1, 1)  # Белый текст
        elif is_today:
            bg_color = (0.92, 0.95, 1, 1)  # Светло-синий для сегодня
            text_color = (0.26, 0.55, 0.96, 1)  # Синий текст

        day_button = Button(
            text=str(day),
            size_hint_y=None,
            height=dp(50),
            background_color=bg_color,
            background_normal='',
            color=text_color,
            font_size='14sp',
            bold=is_today or is_selected
        )

        # Добавляем эффект тени для выбранного дня
        if is_selected:
            day_button.canvas.before.clear()
            with day_button.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(*bg_color)
                RoundedRectangle(
                    pos=(day_button.x + dp(2), day_button.y + dp(2)),
                    size=(day_button.width - dp(4), day_button.height - dp(4)),
                    radius=[dp(20)]
                )

        # Обработчик нажатия
        day_button.bind(on_press=lambda instance: self._on_day_selected(day))

        return day_button

    def _on_day_selected(self, day):
        """Обрабатывает выбор дня."""
        self.selected_day = day
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
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.selected_day = 0
        self._update_calendar()

    def _next_month(self):
        """Переход к следующему месяцу."""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.selected_day = 0
        self._update_calendar()

    def _go_to_today(self):
        """Переход к текущему дню."""
        self.current_date = datetime.now()
        self.selected_day = self.current_date.day
        self._update_calendar()