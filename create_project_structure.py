import os
import glob


def get_project_structure(root_dir):
    """Собирает структуру проекта в текстовый файл"""

    # Игнорируемые папки и файлы
    ignore_dirs = {'__pycache__', '.git', '.idea', 'venv', 'env', 'node_modules'}
    ignore_files = {'.DS_Store', '.gitignore', '*.pyc'}

    output_lines = []

    def should_include(path):
        """Проверяет, нужно ли включать файл/папку в вывод"""
        name = os.path.basename(path)
        if name in ignore_dirs:
            return False
        if any(name.endswith(ext) for ext in ['.pyc', '.tmp']):
            return False
        return True

    def add_file_content(file_path, relative_path):
        """Добавляет содержимое файла в вывод"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            output_lines.append(f"\n{'=' * 80}\n")
            output_lines.append(f"ФАЙЛ: {relative_path}\n")
            output_lines.append(f"{'=' * 80}\n")
            output_lines.append(content)
            output_lines.append(f"\n{'=' * 80}\n")

        except UnicodeDecodeError:
            # Пропускаем бинарные файлы
            output_lines.append(f"\n{'=' * 80}\n")
            output_lines.append(f"ФАЙЛ: {relative_path} (бинарный файл, содержимое пропущено)\n")
            output_lines.append(f"{'=' * 80}\n")
        except Exception as e:
            output_lines.append(f"\n{'=' * 80}\n")
            output_lines.append(f"ФАЙЛ: {relative_path} (ошибка чтения: {str(e)})\n")
            output_lines.append(f"{'=' * 80}\n")

    def traverse_directory(current_dir, prefix=""):
        """Рекурсивно обходит директории"""
        try:
            items = sorted(os.listdir(current_dir))

            for item in items:
                full_path = os.path.join(current_dir, item)
                relative_path = os.path.relpath(full_path, root_dir)

                if not should_include(full_path):
                    continue

                if os.path.isdir(full_path):
                    # Добавляем информацию о папке
                    output_lines.append(f"{prefix}📁 {item}/\n")
                    traverse_directory(full_path, prefix + "    ")
                else:
                    # Добавляем информацию о файле и его содержимое
                    output_lines.append(f"{prefix}📄 {item}\n")
                    add_file_content(full_path, relative_path)

        except PermissionError:
            output_lines.append(f"{prefix}❌ [Нет доступа к папке]\n")
        except Exception as e:
            output_lines.append(f"{prefix}❌ [Ошибка: {str(e)}]\n")

    # Заголовок
    output_lines.append("СТРУКТУРА ПРОЕКТА: SMART PLANNER\n")
    output_lines.append(f"Корневая директория: {root_dir}\n")
    output_lines.append("=" * 80 + "\n")

    # Начинаем обход с корневой директории
    traverse_directory(root_dir)

    return "".join(output_lines)


def save_project_structure():
    """Сохраняет структуру проекта в файл"""

    # Определяем корневую директорию проекта
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Имя выходного файла
    output_file = os.path.join(current_dir, "project_structure.txt")

    print(f"Создание структуры проекта...")
    print(f"Корневая директория: {current_dir}")
    print(f"Выходной файл: {output_file}")

    # Получаем структуру
    structure = get_project_structure(current_dir)

    # Сохраняем в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(structure)

    print(f"✅ Структура проекта сохранена в: {output_file}")
    print(f"📊 Размер файла: {len(structure)} символов")

    # Показываем статистику
    lines = structure.split('\n')
    file_count = structure.count('ФАЙЛ:')
    dir_count = structure.count('📁')

    print(f"📁 Папок: {dir_count}")
    print(f"📄 Файлов: {file_count}")
    print(f"📝 Строк: {len(lines)}")


if __name__ == "__main__":
    save_project_structure()