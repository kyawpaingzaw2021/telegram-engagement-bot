"""In-memory temp state for OTP flow (lost on restart — acceptable)."""
from typing import Any
from telethon import TelegramClient

# user_id → Telethon client (during OTP flow)
temp_clients: dict[int, TelegramClient] = {}

# user_id → phone
temp_phones: dict[int, str] = {}

# user_id → (api_id, api_hash)
temp_api: dict[int, tuple[int, str]] = {}

# user_id → phone_code_hash
temp_code_hash: dict[int, str] = {}

# user_id → label draft
temp_labels: dict[int, str] = {}


def clear(user_id: int) -> None:
    temp_clients.pop(user_id, None)
    temp_phones.pop(user_id, None)
    temp_api.pop(user_id, None)
    temp_code_hash.pop(user_id, None)
    temp_labels.pop(user_id, None)


def get_temp_client(user_id: int) -> TelegramClient | None:
    return temp_clients.get(user_id)


def get_temp_phone(user_id: int) -> str | None:
    return temp_phones.get(user_id)


def get_temp_api(user_id: int) -> tuple[int, str] | None:
    return temp_api.get(user_id)


def get_code_hash(user_id: int) -> str | None:
    return temp_code_hash.get(user_id)


def get_label(user_id: int) -> str | None:
    return temp_labels.get(user_id)
