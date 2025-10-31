from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from datetime import datetime, timedelta
from core.models import Priority
import os

# Импортируем необходимые виджеты
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'task_editor.kv')
Builder.load_file(kv_path)


class TaskEditorScreen(Screen):
    """Экран создания и редактирования задач."""

    def __init__(self, task_service=None, **kwargs):
        super().__init__(**kwargs)
        self.task_service = task_service
        # Устанавливаем дату на завтра по умолчанию
        self.selected_date = datetime.now() + timedelta(days=1)
        self.selected_time = (12, 0)  # (часы, минуты)
        self.reminder_time = None
        Clock.schedule_once(self._setup_initial_state, 0.1)

    def _setup_initial_state(self, dt):
        """Устанавливает начальное состояние формы"""
        if hasattr(self, 'ids') and 'medium_priority' in self.ids:
            self.ids.medium_priority.state = 'down'
        self._update_datetime_display()

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

            # Создаем объект datetime из выбранной даты и времени
            due_date = self.selected_date.replace(
                hour=self.selected_time[0],
                minute=self.selected_time[1],
                second=0,
                microsecond=0
            )

            print(f"Сохранение задачи: {title}")
            print(f"Описание: {description}")
            print(f"Приоритет: {selected_priority_text}")
            print(f"Дата и время: {due_date}")

            # Создаем задачу
            task = self.task_service.create_task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                reminder_time=self.reminder_time
            )

            print(f"Задача успешно создана: {task.title}")
            self._go_to_main()

        except Exception as e:
            print(f"Ошибка сохранения задачи: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"Ошибка: {str(e)}")

    def _show_error(self, message):
        """Показывает сообщение об ошибке"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))

        btn = Button(text='OK', size_hint_y=0.4)
        popup = Popup(title='Ошибка', content=content, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)

        popup.open()

    def _select_date(self):
        """Открывает красивое окно выбора даты"""
        # Создаем модальное окно
        modal = ModalView(
            size_hint=(0.85, 0.7),
            background_color=(0, 0, 0, 0.3),
            overlay_color=(0, 0, 0, 0.5)
        )

        # Основной контейнер
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
            text='Выберите дату',
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

        month_label = Label(
            text=self._get_month_name(self.selected_date.month) + " " + str(self.selected_date.year),
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

        # Заполняем календарь
        self._fill_calendar_grid(calendar_grid, modal)
        main_layout.add_widget(calendar_grid)

        # Кнопки действий
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

        confirm_btn = Button(
            text='Выбрать',
            background_color=(0.2, 0.6, 1, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )

        actions_layout.add_widget(today_btn)
        actions_layout.add_widget(confirm_btn)
        main_layout.add_widget(actions_layout)

        # Обработчики событий
        def select_today(instance):
            self.selected_date = datetime.now()
            self._update_datetime_display()
            modal.dismiss()

        def confirm_selection(instance):
            self._update_datetime_display()
            modal.dismiss()

        def change_month(delta):
            new_month = self.selected_date.month + delta
            new_year = self.selected_date.year

            if new_month > 12:
                new_month = 1
                new_year += 1
            elif new_month < 1:
                new_month = 12
                new_year -= 1

            self.selected_date = self.selected_date.replace(year=new_year, month=new_month, day=1)
            month_label.text = self._get_month_name(self.selected_date.month) + " " + str(self.selected_date.year)
            self._fill_calendar_grid(calendar_grid, modal)

        today_btn.bind(on_press=select_today)
        confirm_btn.bind(on_press=confirm_selection)
        prev_btn.bind(on_press=lambda x: change_month(-1))
        next_btn.bind(on_press=lambda x: change_month(1))

        modal.add_widget(main_layout)
        modal.open()

    def _get_month_name(self, month_num):
        """Возвращает название месяца по номеру"""
        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ""

    def _fill_calendar_grid(self, grid, modal):
        """Заполняет сетку календаря днями"""
        grid.clear_widgets()

        # Получаем первый день месяца и количество дней
        first_day = self.selected_date.replace(day=1)
        days_in_month = self._get_days_in_month(self.selected_date.year, self.selected_date.month)

        # Пустые ячейки до первого дня
        first_weekday = first_day.weekday()
        for _ in range(first_weekday):
            grid.add_widget(Widget())

        # Добавляем дни
        today = datetime.now().date()
        current_month = self.selected_date.month
        current_year = self.selected_date.year

        for day in range(1, days_in_month + 1):
            day_date = datetime(current_year, current_month, day)
            is_today = day_date.date() == today
            is_selected = (day_date.day == self.selected_date.day and
                           day_date.month == self.selected_date.month and
                           day_date.year == self.selected_date.year)

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

            btn.bind(on_press=lambda instance, d=day: self._on_calendar_day_selected(d, modal))
            grid.add_widget(btn)

    def _get_days_in_month(self, year, month):
        """Возвращает количество дней в месяце"""
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        last_day = next_month - timedelta(days=1)
        return last_day.day

    def _on_calendar_day_selected(self, day, modal):
        """Обрабатывает выбор дня в календаре"""
        self.selected_date = self.selected_date.replace(day=day)
        self._update_datetime_display()
        if modal:
            modal.dismiss()

    def _select_time(self):
        """Открывает красивое окно выбора времени"""
        # Используем изменяемый объект для хранения временного выбора
        temp_time = [self.selected_time[0], self.selected_time[1]]

        modal = ModalView(
            size_hint=(0.8, 0.6),
            background_color=(0, 0, 0, 0.3),
            overlay_color=(0, 0, 0, 0.5)
        )

        main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(0),
            padding=dp(20)
        )

        # Заголовок
        header = Label(
            text='Выберите время',
            font_size='20sp',
            bold=True,
            size_hint_y=0.2,
            color=(0.1, 0.15, 0.25, 1)
        )
        main_layout.add_widget(header)

        # Сетка часов и минут
        time_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.6)

        # Часы
        hours_label = Label(text='Часы:', size_hint_y=0.1, color=(0.4, 0.4, 0.4, 1))
        time_layout.add_widget(hours_label)

        hours_grid = GridLayout(cols=6, spacing=dp(5), size_hint_y=0.4)

        # Список для хранения кнопок часов
        hour_buttons = []
        for hour in range(0, 24):
            btn = Button(
                text=str(hour).zfill(2),
                background_color=(0.95, 0.95, 0.95, 1),
                background_normal='',
                color=(0.3, 0.3, 0.3, 1)
            )

            # Выделяем выбранный час
            if hour == temp_time[0]:
                btn.background_color = (0.2, 0.6, 1, 1)
                btn.color = (1, 1, 1, 1)

            def make_hour_handler(h):
                def handler(instance):
                    # Сбрасываем цвет всех кнопок часов
                    for button in hour_buttons:
                        button.background_color = (0.95, 0.95, 0.95, 1)
                        button.color = (0.3, 0.3, 0.3, 1)
                    # Устанавливаем цвет нажатой кнопки
                    instance.background_color = (0.2, 0.6, 1, 1)
                    instance.color = (1, 1, 1, 1)
                    temp_time[0] = h
                    print(f"Выбран час: {h}")

                return handler

            btn.bind(on_press=make_hour_handler(hour))
            hours_grid.add_widget(btn)
            hour_buttons.append(btn)

        time_layout.add_widget(hours_grid)

        # Минуты
        minutes_label = Label(text='Минуты:', size_hint_y=0.1, color=(0.4, 0.4, 0.4, 1))
        time_layout.add_widget(minutes_label)

        minutes_grid = GridLayout(cols=6, spacing=dp(5), size_hint_y=0.4)

        # Список для хранения кнопок минут
        minute_buttons = []
        for minute in range(0, 60, 5):
            btn = Button(
                text=str(minute).zfill(2),
                background_color=(0.95, 0.95, 0.95, 1),
                background_normal='',
                color=(0.3, 0.3, 0.3, 1)
            )

            # Выделяем выбранную минуту
            if minute == temp_time[1]:
                btn.background_color = (0.2, 0.6, 1, 1)
                btn.color = (1, 1, 1, 1)

            def make_minute_handler(m):
                def handler(instance):
                    # Сбрасываем цвет всех кнопок минут
                    for button in minute_buttons:
                        button.background_color = (0.95, 0.95, 0.95, 1)
                        button.color = (0.3, 0.3, 0.3, 1)
                    # Устанавливаем цвет нажатой кнопки
                    instance.background_color = (0.2, 0.6, 1, 1)
                    instance.color = (1, 1, 1, 1)
                    temp_time[1] = m
                    print(f"Выбраны минуты: {m}")

                return handler

            btn.bind(on_press=make_minute_handler(minute))
            minutes_grid.add_widget(btn)
            minute_buttons.append(btn)

        time_layout.add_widget(minutes_grid)

        main_layout.add_widget(time_layout)

        # Кнопки
        buttons_layout = BoxLayout(spacing=dp(10), size_hint_y=0.2)

        cancel_btn = Button(
            text='Отмена',
            background_color=(0.9, 0.9, 0.9, 1),
            background_normal='',
            color=(0.3, 0.3, 0.3, 1)
        )

        ok_btn = Button(
            text='OK',
            background_color=(0.2, 0.6, 1, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )

        def on_ok(instance):
            self.selected_time = (temp_time[0], temp_time[1])
            print(f"Установлено время: {self.selected_time[0]:02d}:{self.selected_time[1]:02d}")
            self._update_datetime_display()
            modal.dismiss()

        def on_cancel(instance):
            modal.dismiss()

        cancel_btn.bind(on_press=on_cancel)
        ok_btn.bind(on_press=on_ok)

        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(ok_btn)
        main_layout.add_widget(buttons_layout)

        modal.add_widget(main_layout)
        modal.open()

    def _update_datetime_display(self):
        """Обновляет отображение даты и времени на кнопках"""
        if hasattr(self, 'ids'):
            # Форматируем дату
            from utils.date_utils import format_date_display
            date_text = format_date_display(self.selected_date)
            time_text = f"{self.selected_time[0]:02d}:{self.selected_time[1]:02d}"

            # Обновляем обе кнопки
            if 'date_button' in self.ids:
                self.ids.date_button.text = date_text
            if 'time_button' in self.ids:
                self.ids.time_button.text = time_text

            print(f"Обновлено отображение: дата={date_text}, время={time_text}")

    def _set_reminder(self):
        """Установка напоминания."""
        print("Установка напоминания...")
        # Устанавливаем напоминание за 30 минут до дедлайна
        due_datetime = self.selected_date.replace(
            hour=self.selected_time[0],
            minute=self.selected_time[1]
        )
        self.reminder_time = due_datetime - timedelta(minutes=30)
        self._show_reminder_set()

    def _show_reminder_set(self):
        """Показывает установленное напоминание"""
        from kivy.uix.popup import Popup
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
            self.selected_date = datetime.now() + timedelta(days=1)
            self.selected_time = (12, 0)
            self.reminder_time = None
            self._update_datetime_display()