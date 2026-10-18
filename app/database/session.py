from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import get_settings
from app.database.models import Base, Exercise
from app.exercises.catalog import CATALOG

_engine = None
_factory = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url)
    return _engine


def session_factory() -> async_sessionmaker[AsyncSession]:
    global _factory
    if _factory is None:
        _factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _factory


async def init_database() -> None:
    async with get_engine().begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with session_factory()() as session:
        if await session.scalar(select(Exercise.id).limit(1)) is None:
            session.add_all([
                Exercise(
                    slug=item.slug,
                    name=item.name,
                    primary_muscles=list(item.primary),
                    secondary_muscles=list(item.secondary),
                    kind=item.kind,
                    equipment=list(item.equipment),
                    difficulty=item.difficulty,
                    rep_min=item.reps[0],
                    rep_max=item.reps[1],
                    alternatives=list(item.alternatives),
                )
                for item in CATALOG.values()
            ])
            await session.commit()


async def close_database() -> None:
    global _engine, _factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _factory = None
