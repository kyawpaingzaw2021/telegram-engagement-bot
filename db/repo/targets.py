from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Target, TargetChannel


async def get_target(db: AsyncSession, user_id: int) -> Target | None:
    result = await db.execute(select(Target).where(Target.user_id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_target(db: AsyncSession, user_id: int) -> Target:
    t = await get_target(db, user_id)
    if t is None:
        t = Target(user_id=user_id)
        db.add(t)
        await db.commit()
        await db.refresh(t)
    return t


async def update_target(db: AsyncSession, user_id: int, **kwargs) -> None:
    t = await get_or_create_target(db, user_id)
    for k, v in kwargs.items():
        setattr(t, k, v)
    await db.commit()


async def get_channels(db: AsyncSession, user_id: int) -> list[TargetChannel]:
    result = await db.execute(
        select(TargetChannel).where(TargetChannel.user_id == user_id).order_by(TargetChannel.id)
    )
    return list(result.scalars().all())


async def get_channel_by_id(db: AsyncSession, cid: int) -> TargetChannel | None:
    result = await db.execute(select(TargetChannel).where(TargetChannel.id == cid))
    return result.scalar_one_or_none()


async def add_channel(db: AsyncSession, user_id: int, username: str) -> TargetChannel:
    ch = TargetChannel(user_id=user_id, channel_username=username)
    db.add(ch)
    await db.commit()
    await db.refresh(ch)
    return ch


async def toggle_channel(db: AsyncSession, cid: int) -> bool:
    ch = await get_channel_by_id(db, cid)
    if not ch:
        return False
    ch.is_active = not ch.is_active
    await db.commit()
    return ch.is_active


async def delete_channel(db: AsyncSession, cid: int) -> None:
    ch = await get_channel_by_id(db, cid)
    if ch:
        await db.delete(ch)
        await db.commit()
