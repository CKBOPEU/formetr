from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot import handlers as base_handlers
from app.bot import handlers_extra
from app.bot import handlers_subscription
from app.bot import handlers_food
from app.bot import handlers_admin
from app.bot import handlers_assistant
from app.bot.access import AccessMiddleware
from app.bot.clean_ui import ReplaceCallbackMessageMiddleware


def enhanced_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽 Составить меню", callback_data="menu:mealplan"), InlineKeyboardButton(text="🥗 Калории и БЖУ", callback_data="menu:nutrition")],
        [InlineKeyboardButton(text="🔎 Продукты", callback_data="menu:foods")],
        [InlineKeyboardButton(text="🚫 Мои ограничения", callback_data="diet:show")],
        [InlineKeyboardButton(text="📏 Замеры", callback_data="menu:measurements"), InlineKeyboardButton(text="📈 Прогресс", callback_data="menu:progress_review")],
        [InlineKeyboardButton(text="🎯 Моя цель", callback_data="menu:goal"), InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        [InlineKeyboardButton(text="✏️ Изменить цель", callback_data="goal:change")],
        [InlineKeyboardButton(text="⭐ FORMETR Pro", callback_data="subscription:status")],
    ])


base_handlers.main_menu = enhanced_main_menu
handlers_extra.main_menu = enhanced_main_menu
router = base_handlers.router
router.callback_query.outer_middleware(AccessMiddleware())
router.callback_query.middleware(ReplaceCallbackMessageMiddleware())
router.message.outer_middleware(AccessMiddleware())
