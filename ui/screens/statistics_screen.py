from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty
import os

kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'statistics_screen.kv')
Builder.load_file(kv_path)


class StatisticsScreen(Screen):
    """Экран статистики продуктивности."""

    completed_tasks = NumericProperty(12)
    productivity_percent = NumericProperty(75)
    chart_data = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _go_to_main(self):
        self.manager.current = 'main'
