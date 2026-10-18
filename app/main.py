import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.bot.handlers_entry import router
from app.config import get_settings
from app.database.session import close_database, init_database


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    await init_database()
    bot = Bot(token=settings.bot_token.get_secret_value())
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await close_database()


def run() -> None:
    asyncio.run(main())
