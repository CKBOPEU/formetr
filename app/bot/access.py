from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.services.subscriptions import access_status


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Оформить FORMETR Pro", callback_data="subscription:buy")],
        [InlineKeyboardButton(text="Моя подписка", callback_data="subscription:status")],
    ])


class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)
        if isinstance(event, CallbackQuery):
            callback = event.data or ""
            protected = callback.startswith(("menu:mealplan", "menu:foods", "menu:nutrition", "menu:measurements", "menu:progress", "food", "portion", "mealplan:", "diet:", "measure:", "review:", "goal:"))
            exempt = callback.startswith("subscription:")
            if protected and not exempt:
                status = await access_status(user.id)
                if not status.allowed:
                    await event.answer()
                    await event.message.answer("Пробный период завершён. Оформите FORMETR Pro, чтобы продолжить.", reply_markup=subscribe_keyboard())
                    return None
        elif isinstance(event, Message):
            text = event.text or ""
            if text.startswith(("/start", "/reset", "/subscribe", "/terms", "/support", "/paysupport")) or event.successful_payment:
                return await handler(event, data)
            state = data.get("state")
            state_name = await state.get_state() if state else None
            if state_name and state_name.startswith("MeasurementEntry:"):
                status = await access_status(user.id)
                if not status.allowed:
                    await event.answer("Пробный период завершён.", reply_markup=subscribe_keyboard())
                    return None
        return await handler(event, data)
