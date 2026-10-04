from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from db.repo.services import get_service, update_service
from db.session import async_session

router = Router()


def _service_kb(s):
    def b(label, key, state):
        return [{"text": f"{label}: {'🟢' if state else '🔴'}", "callback_data": f"svc_toggle:{key}"}]

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    rows = [
        [InlineKeyboardButton(text="🟢 Bot Engine (locked)", callback_data="svc_noop")],
        [InlineKeyboardButton(text=f"Worker: {'🟢' if s.worker_on else '🔴'}", callback_data="svc_toggle:worker_on")],
        [InlineKeyboardButton(text=f"Scheduler: {'🟢' if s.scheduler_on else '🔴'}", callback_data="svc_toggle:scheduler_on")],
        [InlineKeyboardButton(text=f"Ads: {'🟢' if s.ads_on else '🔴'}", callback_data="svc_toggle:ads_on")],
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="svc_refresh")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _render(msg_or_call):
    uid = msg_or_call.from_user.id
    async with async_session() as db:
        s = await get_service(db, uid)
        if s is None:
            await update_service(db, uid)
            s = await get_service(db, uid)

    text = (
        "🎛️ <b>Services</b>\n\n"
        f"🤖 Bot Engine: 🟢 (always on)\n"
        f"⚙️ Worker Engine: {'🟢' if s.worker_on else '🔴'}\n"
        f"⏱️ Scheduler: {'🟢' if s.scheduler_on else '🔴'}\n"
        f"📺 Ads Engine: {'🟢' if s.ads_on else '🔴'}"
    )
    kb = _service_kb(s)
    if isinstance(msg_or_call, CallbackQuery):
        try:
            await msg_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await msg_or_call.message.answer(text, reply_markup=kb)
    else:
        await msg_or_call.answer(text, reply_markup=kb)


@router.message(F.text == "🎛️ Services")
async def open_services(message: Message):
    await _render(message)


@router.callback_query(F.data == "svc_refresh")
async def svc_refresh(call: CallbackQuery):
    await _render(call)
    await call.answer()


@router.callback_query(F.data.startswith("svc_toggle:"))
async def svc_toggle(call: CallbackQuery):
    key = call.data.split(":")[1]
    async with async_session() as db:
        s = await get_service(db, call.from_user.id)
        new_val = not getattr(s, key)
        await update_service(db, call.from_user.id, **{key: new_val})
    await call.answer(f"{'🟢 ON' if new_val else '🔴 OFF'}")
    await _render(call)


@router.callback_query(F.data == "svc_noop")
async def svc_noop(call: CallbackQuery):
    await call.answer("Bot Engine ကို မပိတ်နိုင်ဘူး", show_alert=True)
