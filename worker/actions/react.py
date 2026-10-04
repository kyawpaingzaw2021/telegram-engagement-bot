import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

from core.logger import logger
from worker.actions.channel import ensure_membership

REACTIONS = ["👍", "❤️", "🔥", "🎉", "😍", "👏", "🥰", "😁", "🤩", "💯"]


async def react_posts(client: TelegramClient, channel: str, count: int) -> int:
    ok = await ensure_membership(client, channel)
    if not ok:
        logger.warning(f"react: skip {channel}")
        return 0

    try:
        entity = await client.get_entity(channel)
        posts = await client.get_messages(entity, limit=count)
    except Exception as e:
        logger.warning(f"react: setup failed {channel}: {e}")
        return 0

    done = 0
    for post in posts:
        if not post or not post.id:
            continue
        try:
            await client(SendReactionRequest(
                peer=entity,
                msg_id=post.id,
                reaction=[ReactionEmoji(emoticon=random.choice(REACTIONS))],
            ))
            done += 1
            await asyncio.sleep(random.uniform(5, 12))
        except Exception as e:
            logger.debug(f"react err: {e}")
    return done
