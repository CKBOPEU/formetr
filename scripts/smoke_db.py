import asyncio

from sqlalchemy import func, select

from app.database.models import Exercise
from app.database.session import close_database, init_database, session_factory


async def main() -> None:
    await init_database()
    async with session_factory()() as session:
        count = await session.scalar(select(func.count(Exercise.id)))
        print(f"seeded exercises: {count}")
        if not count:
            raise RuntimeError("Exercise catalog was not seeded")
    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
