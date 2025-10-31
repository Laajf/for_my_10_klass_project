from datetime import datetime, timedelta


def format_date_display(date: datetime) -> str:
    """Форматирует дату для отображения в современном стиле"""
    if not isinstance(date, datetime):
        return "Не указано"

    today = datetime.now().date()
    target_date = date.date()

    if target_date == today:
        return "Сегодня"
    elif target_date == today + timedelta(days=1):
        return "Завтра"
    elif target_date == today - timedelta(days=1):
        return "Вчера"
    else:
        # Короткий формат: "30 окт"
        month_names = ["янв", "фев", "мар", "апр", "май", "июн",
                       "июл", "авг", "сен", "окт", "ноя", "дек"]
        return f"{date.day} {month_names[date.month - 1]}"


def format_time_display(date: datetime) -> str:
    """Форматирует время для отображения"""
    if not isinstance(date, datetime):
        return "Не указано"
    return date.strftime("%H:%M")


def is_date_in_future(date: datetime) -> bool:
    """Проверяет, что дата в будущем"""
    return date > datetime.now()