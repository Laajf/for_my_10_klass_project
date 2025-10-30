import os

# Пути к файлам данных
DATA_DIR = os.path.join(os.path.expanduser("~"), ".smart_planner")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
STATISTICS_FILE = os.path.join(DATA_DIR, "statistics.json")

# Настройки уведомлений
REMINDER_BEFORE_MINUTES = 30

# Цвета приоритетов
PRIORITY_COLORS = {
    "Высокий": (0.8, 0.2, 0.2, 1),
    "Средний": (0.9, 0.6, 0.1, 1), 
    "Низкий": (0.2, 0.6, 0.2, 1)
}

def ensure_data_dir():
    """Создает директорию для данных если она не существует"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)