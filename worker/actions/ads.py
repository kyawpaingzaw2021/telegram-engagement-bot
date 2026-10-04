from telethon import TelegramClient
from core.logger import logger
from worker.actions.channel import ensure_membership
from worker.actions.react import react_posts
from worker.actions.view import view_posts


async def run_ads(client: TelegramClient, ads_channel: str, count: int) -> bool:
    if not ads_channel:
        return False

    ok = await ensure_membership(client, ads_channel)
    if not ok:
        logger.warning(f"ads: skip {ads_channel}")
        return False

    try:
        await view_posts(client, ads_channel, count)
        await react_posts(client, ads_channel, count)
        return True
    except Exception as e:
        logger.warning(f"ads err {ads_channel}: {e}")
        return False
