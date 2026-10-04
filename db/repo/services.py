from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Service


async def get_service(db: AsyncSession, user_id: int) -> Service | None:
    result = await db.execute(select(Service).where(Service.user_id == user_id))
    return result.scalar_one_or_none()


async def update_service(db: AsyncSession, user_id: int, **kwargs) -> None:
    s = await get_service(db, user_id)
    if s is None:
        s = Service(user_id=user_id)
        db.add(s)
    for k, v in kwargs.items():
        setattr(s, k, v)
    await db.commit()
