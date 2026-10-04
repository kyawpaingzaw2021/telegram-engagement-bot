from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Service


async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    username: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)

        service = Service(user_id=telegram_id)
        db.add(service)

        await db.commit()
        await db.refresh(user)

    return user


async def get_user(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, telegram_id: int, **kwargs) -> None:
    user = await get_user(db, telegram_id)
    if user is None:
        return
    for key, value in kwargs.items():
        setattr(user, key, value)
    await db.commit()
