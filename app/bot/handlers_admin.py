from aiogram.filters import Command
from aiogram.types import Message

from app.bot.handlers import router
from app.config import get_settings
from app.services.subscriptions import grant_free_access, revoke_free_access


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_id_set


def _target_id(message: Message) -> int | None:
    parts = (message.text or "").split()
    return int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None


@router.message(Command("admin"))
async def admin_help(message: Message) -> None:
    if not _is_admin(message.from_user.id): return
    await message.answer("Управление доступом:\n/grant TELEGRAM_ID — выдать бесплатно\n/revoke TELEGRAM_ID — отозвать\n\nВаш ID: " + str(message.from_user.id))


@router.message(Command("grant"))
async def grant_access(message: Message) -> None:
    if not _is_admin(message.from_user.id): return
    target = _target_id(message)
    if not target: return await message.answer("Формат: /grant 123456789")
    await grant_free_access(target, message.from_user.id)
    await message.answer(f"✅ Пользователю {target} выдан бессрочный бесплатный доступ.")


@router.message(Command("revoke"))
async def revoke_access(message: Message) -> None:
    if not _is_admin(message.from_user.id): return
    target = _target_id(message)
    if not target: return await message.answer("Формат: /revoke 123456789")
    removed = await revoke_free_access(target)
    await message.answer("Доступ отозван." if removed else "У пользователя не было отдельного бесплатного доступа.")
