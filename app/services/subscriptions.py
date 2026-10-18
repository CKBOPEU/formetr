from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select

from app.config import get_settings
from app.database.models import FreeAccessGrant, Subscription, User
from app.database.session import session_factory


@dataclass(frozen=True)
class AccessStatus:
    allowed: bool
    kind: str
    expires_at: datetime | None
    days_left: int


def _days_left(end: datetime | None, now: datetime) -> int:
    if not end or end <= now:
        return 0
    seconds = (end - now).total_seconds()
    return max(1, int((seconds + 86399) // 86400))


async def access_status(telegram_id: int) -> AccessStatus:
    now = datetime.utcnow()
    async with session_factory()() as session:
        if telegram_id in get_settings().admin_id_set:
            return AccessStatus(True, "admin", None, 0)
        grant = await session.scalar(select(FreeAccessGrant).where(FreeAccessGrant.telegram_id == telegram_id))
        if grant:
            return AccessStatus(True, "free", None, 0)
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return AccessStatus(True, "onboarding", None, 0)
        subscription = await session.scalar(select(Subscription).where(Subscription.user_id == user.id))
        if not subscription:
            trial_end = user.created_at + timedelta(days=get_settings().trial_days)
            subscription = Subscription(user_id=user.id, status="trial", trial_ends_at=trial_end)
            session.add(subscription)
            await session.commit()
        if subscription.current_period_end and subscription.current_period_end > now:
            return AccessStatus(True, "paid", subscription.current_period_end, _days_left(subscription.current_period_end, now))
        if subscription.trial_ends_at > now:
            return AccessStatus(True, "trial", subscription.trial_ends_at, _days_left(subscription.trial_ends_at, now))
        if subscription.status != "expired":
            subscription.status = "expired"
            await session.commit()
        return AccessStatus(False, "expired", subscription.trial_ends_at, 0)


async def activate_subscription(
    telegram_id: int,
    charge_id: str,
    expiration_timestamp: int | None,
    is_recurring: bool,
) -> datetime:
    now = datetime.utcnow()
    period_end = datetime.utcfromtimestamp(expiration_timestamp) if expiration_timestamp else now + timedelta(days=30)
    async with session_factory()() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            raise ValueError("User not found")
        subscription = await session.scalar(select(Subscription).where(Subscription.user_id == user.id))
        if not subscription:
            subscription = Subscription(user_id=user.id, status="active", trial_ends_at=now)
            session.add(subscription)
        subscription.status = "active"
        subscription.current_period_end = period_end
        subscription.telegram_payment_charge_id = charge_id
        subscription.is_recurring = is_recurring
        await session.commit()
    return period_end


async def grant_free_access(telegram_id: int, granted_by: int, note: str | None = None) -> None:
    async with session_factory()() as session:
        grant = await session.scalar(select(FreeAccessGrant).where(FreeAccessGrant.telegram_id == telegram_id))
        if not grant:
            session.add(FreeAccessGrant(telegram_id=telegram_id, granted_by=granted_by, note=note))
        else:
            grant.granted_by = granted_by
            grant.note = note
        await session.commit()


async def revoke_free_access(telegram_id: int) -> bool:
    async with session_factory()() as session:
        grant = await session.scalar(select(FreeAccessGrant).where(FreeAccessGrant.telegram_id == telegram_id))
        if not grant:
            return False
        await session.delete(grant)
        await session.commit()
        return True
