import asyncio
from core.logger import logger
from db.repo.services import get_service
from db.session import async_session
from worker.runner import run_all


async def scheduler_loop(interval: int = 60):
    logger.info("scheduler started")
    while True:
        try:
            async with async_session() as db:
                # check if any user has scheduler on
                from sqlalchemy import select
                from db.models import Service
                result = await db.execute(select(Service).where(Service.scheduler_on == True))
                services = list(result.scalars().all())

            if services:
                await run_all()
        except Exception as e:
            logger.error(f"scheduler err: {e}")

        await asyncio.sleep(interval)
