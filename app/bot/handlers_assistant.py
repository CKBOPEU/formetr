from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.handlers import router
from app.database.repositories import get_dashboard, measurement_history, save_dietary_preferences
from app.food.catalog import FOODS
from app.services.assistant import answer_question
from app.services.dietary_preferences import parse_exclusions


def assistant_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Мои ограничения", callback_data="diet:show")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:home")],
    ])


@router.message(F.text & ~F.text.startswith("/"))
async def free_text_assistant(message: Message) -> None:
    dashboard = await get_dashboard(message.from_user.id)
    if not dashboard:
        return await message.answer("Сначала создайте профиль командой /start.")
    text = (message.text or "").strip()
    lowered = text.lower()
    exclusions = parse_exclusions(text)
    preference_intent = any(phrase in lowered for phrase in ("не ем", "не люблю", "аллерг", "неперенос", "нельзя мне"))
    if preference_intent and exclusions:
        await save_dietary_preferences(message.from_user.id, text, exclusions)
        names = ", ".join(FOODS[slug].name for slug in exclusions)
        return await message.answer(
            f"✅ Я сохранил ограничения: {names}. Следующее меню будет составлено без них. При аллергии дополнительно проверяйте этикетки.",
            reply_markup=assistant_home(),
        )
    history = await measurement_history(message.from_user.id)
    nutrition = dashboard[3]
    answer = answer_question(text, nutrition.calories if nutrition else None, dashboard[1].kind, len(history))
    await message.answer(answer, reply_markup=assistant_home())
