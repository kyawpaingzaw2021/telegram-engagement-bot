from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from db.repo.users import get_user, update_user
from db.session import async_session

router = Router()


def _timer_kb(on: bool):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔴 Turn OFF" if on else "🟢 Turn ON",
                callback_data="timer_toggle",
            )],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="timer_refresh")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")],
        ]
    )


async def _render(msg_or_call):
    uid = msg_or_call.from_user.id
    async with async_session() as db:
        user = await get_user(db, uid)
    text = (
        "⏱️ <b>Timer</b>\n\n"
        f"Status: {'🟢 ON' if user.timer_on else '🔴 OFF'}\n"
        f"Delay: {user.delay_minutes}m\n"
        f"View: {user.view_count} | React: {user.react_count} | Ads: {user.ads_count}"
    )
    kb = _timer_kb(user.timer_on)
    if isinstance(msg_or_call, CallbackQuery):
        try:
            await msg_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await msg_or_call.message.answer(text, reply_markup=kb)
    else:
        await msg_or_call.answer(text, reply_markup=kb)


@router.message(F.text == "⏱️ Timer")
async def open_timer(message: Message):
    await _render(message)


@router.callback_query(F.data == "timer_refresh")
async def timer_refresh(call: CallbackQuery):
    await _render(call)
    await call.answer()


@router.callback_query(F.data == "timer_toggle")
async def timer_toggle(call: CallbackQuery):
    async with async_session() as db:
        user = await get_user(db, call.from_user.id)
        new_val = not user.timer_on
        await update_user(db, call.from_user.id, timer_on=new_val)
    await call.answer(f"Timer {'🟢 ON' if new_val else '🔴 OFF'}")
    await _render(call)
