import asyncio
from datetime import datetime, timedelta, timezone

from core.logger import logger
from core.session_manager import make_client
from db.repo.services import get_service
from db.repo.sessions import get_active_sessions, update_session
from db.repo.targets import get_channels, get_target
from db.repo.users import get_user
from db.session import async_session
from worker.actions.ads import run_ads
from worker.actions.react import react_posts
from worker.actions.view import view_posts


async def _load_session_data(session_id: int) -> dict | None:
    async with async_session() as db:
        sessions = await get_active_sessions(db)
        s = next((x for x in sessions if x.id == session_id), None)
        if not s:
            return None
        user = await get_user(db, s.user_id)
        target = await get_target(db, s.user_id)
        channels = await get_channels(db, s.user_id)
        svc = await get_service(db, s.user_id)

        return {
            "session": s,
            "user": user,
            "target": target,
            "channels": [c for c in channels if c.is_active],
            "service": svc,
        }


async def run_one_session(session_id: int):
    data = await _load_session_data(session_id)
    if not data:
        return

    s = data["session"]
    user = data["user"]
    target = data["target"]
    channels = data["channels"]
    svc = data["service"]

    if not svc or not svc.worker_on:
        return
    if not user.timer_on:
        return
    if not user.api_id or not user.api_hash:
        return

    logger.info(f"run session {s.label}")

    client = make_client(s.session_string, user.api_id, user.api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise Exception("Session not authorized")

        # Target channels
        for ch in channels:
            try:
                await view_posts(client, ch.channel_username, user.view_count)
                await react_posts(client, ch.channel_username, user.react_count)
                await asyncio.sleep(10)
            except Exception as e:
                logger.warning(f"channel {ch.channel_username}: {e}")

        # Ads
        if svc.ads_on and target and target.ads_channel:
            await run_ads(client, target.ads_channel, user.ads_count)

        await client.disconnect()

        async with async_session() as db:
            await update_session(
                db,
                s.id,
                last_run_at=datetime.now(timezone.utc),
                next_run_at=datetime.now(timezone.utc) + timedelta(minutes=user.delay_minutes),
                status="active",
                last_error=None,
            )
    except Exception as e:
        err_name = type(e).__name__
        logger.error(f"session {s.label} error: {err_name}: {e}")

        dead = ("AuthKeyUnregistered", "UserDeactivated", "SessionRevoked", "AuthKeyDuplicated", "PhoneNumberBanned")
        is_dead = any(k in err_name for k in dead)

        async with async_session() as db:
            if is_dead:
                from db.repo.sessions import delete_session
                await delete_session(db, s.id)
            else:
                await update_session(db, s.id, status="error", last_error=str(e))
        try:
            await client.disconnect()
        except Exception:
            pass


async def run_all():
    async with async_session() as db:
        sessions = await get_active_sessions(db)

    for s in sessions:
        try:
            await run_one_session(s.id)
        except Exception as e:
            logger.error(f"runner loop err: {e}")
        await asyncio.sleep(2)
