import json
import os
from datetime import datetime


def debug_tasks():
    """Проверяет содержимое файла tasks.json"""
    data_file = os.path.join(os.path.expanduser("~"), ".smart_planner", "tasks.json")

    if not os.path.exists(data_file):
        print("Файл tasks.json не существует!")
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            tasks = json.load(f)
            print(f"Найдено задач: {len(tasks)}")

            for i, task in enumerate(tasks):
                print(f"\n--- Задача {i + 1} ---")
                print(f"ID: {task.get('id', 'N/A')}")
                print(f"Название: {task.get('title', 'N/A')}")
                print(f"Статус: {task.get('status', 'N/A')}")
                print(f"Дата выполнения: {task.get('due_date', 'N/A')}")
                print(f"Описание: {task.get('description', 'N/A')}")

        except Exception as e:
            print(f"Ошибка чтения файла: {e}")


if __name__ == "__main__":
    debug_tasks()