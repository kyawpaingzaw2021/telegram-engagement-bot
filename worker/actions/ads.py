import asyncio
import random
from telethon import TelegramClient
from core.logger import logger
from worker.actions.view import view_posts
from worker.actions.react import react_posts


async def run_ads(client: TelegramClient, ads_channel: str, count: int) -> bool:
    if not ads_channel:
        return False
    try:
        entity = await client.get_entity(ads_channel)
        me = await client.get_me()
        try:
            member = await client.get_permissions(entity, me)
            if not member:
                await client(functions.channels.JoinChannelRequest(entity))
                await asyncio.sleep(random.uniform(5, 10))
        except Exception:
            try:
                await client(functions.channels.JoinChannelRequest(entity))
                await asyncio.sleep(random.uniform(5, 10))
            except Exception:
                pass

        await view_posts(client, ads_channel, count)
        await react_posts(client, ads_channel, count)
        return True
    except Exception as e:
        logger.warning(f"ads err {ads_channel}: {e}")
        return False
