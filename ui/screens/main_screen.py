from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # TODO: Добавить красивый UI главного экрана
        # TODO: Список задач, кнопки добавления/навигации
        # TODO: Интегрировать с TaskService для отображения задач

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Главный экран Smart Planner"))
        self.add_widget(layout)