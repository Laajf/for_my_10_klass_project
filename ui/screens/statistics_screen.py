from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
import os

# Загружаем KV-файл
kv_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'statistics_screen.kv')
Builder.load_file(kv_path)


class StatisticsScreen(Screen):
    """Экран статистики продуктивности."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _go_to_main(self):
        self.manager.current = 'main'