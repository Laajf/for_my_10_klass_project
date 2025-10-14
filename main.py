from kivy.app import App
from kivy.uix.screenmanager import ScreenManager


class SmartPlannerApp(App):
    def build(self):
        from ui.screens.main_screen import MainScreen
        from ui.screens.task_editor import TaskEditorScreen
        from ui.screens.calendar_view import CalendarScreen
        from ui.screens.statistics_screen import StatisticsScreen

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(TaskEditorScreen(name='task_editor'))
        sm.add_widget(CalendarScreen(name='calendar'))
        sm.add_widget(StatisticsScreen(name='statistics'))

        return sm


if __name__ == '__main__':
    SmartPlannerApp().run()