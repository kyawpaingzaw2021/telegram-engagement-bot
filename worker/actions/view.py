import asyncio
import random
from telethon import TelegramClient
from core.logger import logger


async def view_posts(client: TelegramClient, channel: str, count: int) -> int:
    try:
        posts = await client.get_messages(channel, limit=count)
    except Exception as e:
        logger.warning(f"view: get_messages failed {channel}: {e}")
        return 0

    done = 0
    for post in posts:
        if not post or not post.id:
            continue
        try:
            await client.get_messages(channel, ids=post.id)
            done += 1
            await asyncio.sleep(random.uniform(3, 8))
        except Exception as e:
            logger.debug(f"view err: {e}")
    return done
