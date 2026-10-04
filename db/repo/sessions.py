from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Session


async def get_sessions(db: AsyncSession, user_id: int) -> list[Session]:
    result = await db.execute(
        select(Session).where(Session.user_id == user_id).order_by(Session.id)
    )
    return list(result.scalars().all())


async def get_session_by_id(db: AsyncSession, session_id: int) -> Session | None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def create_session(
    db: AsyncSession,
    user_id: int,
    label: str,
    phone: str,
    session_string: str,
) -> Session:
    session = Session(
        user_id=user_id,
        label=label,
        phone=phone,
        session_string=session_string,
        status="active",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def update_session(db: AsyncSession, session_id: int, **kwargs) -> None:
    session = await get_session_by_id(db, session_id)
    if session is None:
        return
    for key, value in kwargs.items():
        setattr(session, key, value)
    await db.commit()


async def delete_session(db: AsyncSession, session_id: int) -> None:
    session = await get_session_by_id(db, session_id)
    if session:
        await db.delete(session)
        await db.commit()


async def get_active_sessions(db: AsyncSession) -> list[Session]:
    result = await db.execute(select(Session).where(Session.status == "active"))
    return list(result.scalars().all())
