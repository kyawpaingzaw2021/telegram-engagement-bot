from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from db.repo.services import get_service
from db.repo.sessions import get_sessions
from db.repo.users import get_user
from db.session import async_session

router = Router()


def _status_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Run Now", callback_data="status_run_now")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="status_refresh")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")],
        ]
    )


async def _render(msg_or_call):
    uid = msg_or_call.from_user.id
    async with async_session() as db:
        user = await get_user(db, uid)
        svc = await get_service(db, uid)
        sessions = await get_sessions(db, uid)

    text = (
        "📊 <b>Status</b>\n\n"
        f"⏱️ Timer: {'🟢' if user.timer_on else '🔴'}\n"
        f"⚙️ Worker: {'🟢' if svc.worker_on else '🔴'}\n"
        f"⏱️ Scheduler: {'🟢' if svc.scheduler_on else '🔴'}\n"
        f"📺 Ads: {'🟢' if svc.ads_on else '🔴'}\n\n"
        f"📱 Sessions: {len(sessions)}\n"
    )
    for i, s in enumerate(sessions[:10], 1):
        emoji = "🟢" if s.status == "active" else "🟡" if s.status == "error" else "🔴"
        last = s.last_run_at.strftime("%H:%M") if s.last_run_at else "—"
        text += f"{i}. {emoji} <b>{s.label}</b> — {last}\n"

    kb = _status_kb()
    if isinstance(msg_or_call, CallbackQuery):
        try:
            await msg_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await msg_or_call.message.answer(text, reply_markup=kb)
    else:
        await msg_or_call.answer(text, reply_markup=kb)


@router.message(F.text == "📊 Status")
async def open_status(message: Message):
    await _render(message)


@router.callback_query(F.data == "status_refresh")
async def status_refresh(call: CallbackQuery):
    await _render(call)
    await call.answer()


@router.callback_query(F.data == "status_run_now")
async def status_run_now(call: CallbackQuery):
    await call.answer("⚠️ Worker ကို မရေးရသေးဘူး", show_alert=True)
