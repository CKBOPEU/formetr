from urllib.parse import quote_plus

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choices(items: list[tuple[str, str]], prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"{prefix}:{value}")] for label, value in items])


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка", callback_data="menu:workout"), InlineKeyboardButton(text="🥗 Питание", callback_data="menu:nutrition")],
        [InlineKeyboardButton(text="📏 Замеры", callback_data="menu:measurements"), InlineKeyboardButton(text="📈 Прогресс", callback_data="menu:progress")],
        [InlineKeyboardButton(text="🎯 Моя цель", callback_data="menu:goal"), InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        [InlineKeyboardButton(text="✏️ Изменить цель", callback_data="goal:change")],
    ])


def plan_actions(plan: dict) -> InlineKeyboardMarkup:
    rows = []
    for day in plan["days"]:
        for exercise in day["exercises"]:
            video_query = quote_plus(f"{exercise['name']} правильная техника коротко")
            rows.append([
                InlineKeyboardButton(
                    text=f"▶️ Д{day['day']} · {exercise['name']}",
                    url=f"https://www.youtube.com/results?search_query={video_query}",
                ),
                InlineKeyboardButton(text="🔄", callback_data=f"replace:{day['day']}:{exercise['slug']}"),
            ])
    rows.append([InlineKeyboardButton(text="← Меню", callback_data="menu:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def goal_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить цель", callback_data="goal:change")]])


def review_actions(percent: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить план", callback_data=f"review:apply:{percent}"), InlineKeyboardButton(text="Оставить как есть", callback_data=f"review:keep:{percent}")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ])
