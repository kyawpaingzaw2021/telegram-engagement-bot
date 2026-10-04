from aiogram import Router

from bot.handlers import (
    sessions,
    settings,
    start,
    services,
    status,
    targets,
    timer,
)


def register_handlers(dp_root: Router) -> None:
    dp_root.include_router(start.router)
    dp_root.include_router(settings.router)
    dp_root.include_router(sessions.router)
    dp_root.include_router(targets.router)
    dp_root.include_router(services.router)
    dp_root.include_router(timer.router)
    dp_root.include_router(status.router)
