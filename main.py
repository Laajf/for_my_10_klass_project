from kivy.app import App
from kivy.uix.screenmanager import ScreenManager


class SmartPlannerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_service = None
        self.selected_task_id = None  # Для хранения выбранной задачи из календаря

    def build(self):
        from ui.screens.main_screen import MainScreen
        from ui.screens.task_editor import TaskEditorScreen
        from ui.screens.calendar_view import CalendarScreen
        from ui.screens.statistics_screen import StatisticsScreen

        # Инициализируем сервисы
        from services.task_service import TaskService
        self.task_service = TaskService()

        # Передаем сервисы в экраны
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main', task_service=self.task_service))
        sm.add_widget(TaskEditorScreen(name='task_editor', task_service=self.task_service))
        sm.add_widget(CalendarScreen(name='calendar', task_service=self.task_service))
        sm.add_widget(StatisticsScreen(name='statistics', task_service=self.task_service))

        # Сохраняем ссылку на менеджер для доступа из экранов
        self.sm = sm
        return sm


if __name__ == '__main__':
    SmartPlannerApp().run()