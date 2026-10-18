from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery


class ReplaceCallbackMessageMiddleware(BaseMiddleware):
    """Keep only the next screen after an inline-button choice."""

    async def __call__(self, handler, event, data):
        keep_screen = isinstance(event, CallbackQuery) and (event.data or "").startswith(("replace:", "portion:"))
        if isinstance(event, CallbackQuery) and event.message and not keep_screen:
            try:
                await event.message.delete()
            except TelegramBadRequest:
                # A stale/already deleted message must not break navigation.
                pass
        return await handler(event, data)
