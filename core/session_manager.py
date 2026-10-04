from telethon import TelegramClient
from telethon.sessions import StringSession

from db.models import User


def make_client(session_string: str, api_id: int, api_hash: str) -> TelegramClient:
    return TelegramClient(StringSession(session_string), api_id, api_hash)


def make_temp_client(api_id: int, api_hash: str) -> TelegramClient:
    return TelegramClient(StringSession(), api_id, api_hash)
