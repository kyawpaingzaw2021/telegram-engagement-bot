from aiogram import Router

from bot.handlers import start


def register_handlers(dp_root: Router) -> None:
    dp_root.include_router(start.router)
