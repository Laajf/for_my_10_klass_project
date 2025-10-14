from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from ui.screens.main_screen import MainScreen


class SmartPlannerApp(App):
    def build(self):
        # Создаем менеджер экранов и добавляем главный экран
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    SmartPlannerApp().run()
