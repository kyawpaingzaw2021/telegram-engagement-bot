import asyncio
import random
from telethon import TelegramClient
from telethon.tl import functions
from core.logger import logger


async def ensure_membership(client: TelegramClient, channel: str) -> bool:
    """Channel member ဖြစ်အောင် စစ်/join။ Already member ဆို skip."""
    try:
        entity = await client.get_entity(channel)
        me = await client.get_me()

        try:
            perm = await client.get_permissions(entity, me)
            if perm is not None:
                return True
        except Exception:
            pass

        try:
            await client(functions.channels.JoinChannelRequest(entity))
            await asyncio.sleep(random.uniform(5, 10))
            logger.info(f"joined {channel}")
            return True
        except Exception as e:
            err = type(e).__name__
            if "UserAlreadyParticipant" in err or "AlreadyParticipant" in err:
                return True
            logger.warning(f"join failed {channel}: {e}")
            return False
    except Exception as e:
        logger.warning(f"ensure_membership {channel}: {e}")
        return False
