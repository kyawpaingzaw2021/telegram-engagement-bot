from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import cancel_kb
from bot.keyboards.targets import (
    channels_list_kb,
    single_field_kb,
    targets_menu,
)
from db.repo.targets import (
    add_channel,
    delete_channel,
    get_channels,
    get_target,
    toggle_channel,
    update_target,
)
from db.session import async_session

router = Router()


class TargetSG(StatesGroup):
    bot = State()
    ads = State()
    channel_add = State()


async def _render_targets(msg_or_call):
    uid = msg_or_call.from_user.id
    async with async_session() as db:
        target = await get_target(db, uid)
        channels = await get_channels(db, uid)

    if target is None:
        from db.repo.targets import get_or_create_target
        async with async_session() as db:
            target = await get_or_create_target(db, uid)

    text = (
        "🎯 <b>Targets</b>\n\n"
        f"🤖 Target Bot: {target.target_bot or '—'}\n"
        f"📢 Channels: {len(channels)}\n"
        f"📺 Ads Channel: {target.ads_channel or '—'}"
    )
    kb = targets_menu(target, len(channels))
    if isinstance(msg_or_call, CallbackQuery):
        try:
            await msg_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await msg_or_call.message.answer(text, reply_markup=kb)
    else:
        await msg_or_call.answer(text, reply_markup=kb)


@router.message(F.text == "🎯 Targets")
async def open_targets(message: Message, state: FSMContext):
    await state.clear()
    await _render_targets(message)


@router.callback_query(F.data == "tgt_back")
async def tgt_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await _render_targets(call)
    await call.answer()


# ---------- Bot ----------
@router.callback_query(F.data == "tgt_bot")
async def tgt_bot(call: CallbackQuery):
    await call.message.edit_text(
        "🤖 <b>Target Bot</b>\n\n"
        "Action ရွေးပါ:",
        reply_markup=single_field_kb("bot"),
    )
    await call.answer()


@router.callback_query(F.data == "tgt_change:bot")
async def tgt_bot_change(call: CallbackQuery, state: FSMContext):
    await state.set_state(TargetSG.bot)
    await call.message.edit_text(
        "🤖 Bot username ပို့ပါ (ဥပမာ — <code>@somebot</code>)",
        reply_markup=cancel_kb("tgt_back"),
    )
    await call.answer()


@router.message(TargetSG.bot)
async def tgt_bot_save(message: Message, state: FSMContext):
    val = (message.text or "").strip()
    async with async_session() as db:
        await update_target(db, message.from_user.id, target_bot=val)
    await state.clear()
    await message.answer(f"✅ Bot = <code>{val}</code>")
    await _render_targets(message)


@router.callback_query(F.data == "tgt_remove:bot")
async def tgt_bot_remove(call: CallbackQuery):
    async with async_session() as db:
        await update_target(db, call.from_user.id, target_bot=None)
    await _render_targets(call)
    await call.answer("🗑️ Removed")


# ---------- Ads ----------
@router.callback_query(F.data == "tgt_ads")
async def tgt_ads(call: CallbackQuery):
    await call.message.edit_text(
        "📺 <b>Ads Channel</b>\n\nAction ရွေးပါ:",
        reply_markup=single_field_kb("ads"),
    )
    await call.answer()


@router.callback_query(F.data == "tgt_change:ads")
async def tgt_ads_change(call: CallbackQuery, state: FSMContext):
    await state.set_state(TargetSG.ads)
    await call.message.edit_text(
        "📺 Ads channel username ပို့ပါ (ဥပမာ — <code>@adsch</code>)",
        reply_markup=cancel_kb("tgt_back"),
    )
    await call.answer()


@router.message(TargetSG.ads)
async def tgt_ads_save(message: Message, state: FSMContext):
    val = (message.text or "").strip()
    async with async_session() as db:
        await update_target(db, message.from_user.id, ads_channel=val)
    await state.clear()
    await message.answer(f"✅ Ads = <code>{val}</code>")
    await _render_targets(message)


@router.callback_query(F.data == "tgt_remove:ads")
async def tgt_ads_remove(call: CallbackQuery):
    async with async_session() as db:
        await update_target(db, call.from_user.id, ads_channel=None)
    await _render_targets(call)
    await call.answer("🗑️ Removed")


# ---------- Channels ----------
@router.callback_query(F.data.startswith("tgt_ch_list:"))
async def tgt_ch_list(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    async with async_session() as db:
        channels = await get_channels(db, call.from_user.id)

    text = f"📢 <b>Target Channels</b> ({len(channels)})\n\n"
    if not channels:
        text += "ဘာ channel မှ မရှိသေး။ ➕ Add နှိပ်။"
    else:
        text += f"Page {page+1}/{(len(channels)-1)//5 + 1}\n\n"
        text += "🟢 = active | 🔴 = inactive\nChannel ကို နှိပ်ရင် on/off ပြောင်း"

    await call.message.edit_text(text, reply_markup=channels_list_kb(channels, page))
    await call.answer()


@router.callback_query(F.data.startswith("tgt_ch_toggle:"))
async def tgt_ch_toggle(call: CallbackQuery):
    _, cid, page = call.data.split(":")
    async with async_session() as db:
        new_state = await toggle_channel(db, int(cid))
    await call.answer(f"{'🟢 ON' if new_state else '🔴 OFF'}")
    await tgt_ch_list(call)


@router.callback_query(F.data.startswith("tgt_ch_del:"))
async def tgt_ch_del(call: CallbackQuery):
    _, cid, page = call.data.split(":")
    async with async_session() as db:
        await delete_channel(db, int(cid))
    await call.answer("🗑️ Removed")
    await tgt_ch_list(call)


@router.callback_query(F.data == "tgt_ch_add")
async def tgt_ch_add_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(TargetSG.channel_add)
    await call.message.edit_text(
        "📢 Channel username ပို့ပါ (ဥပမာ — <code>@channelname</code>)",
        reply_markup=cancel_kb("tgt_back"),
    )
    await call.answer()


@router.message(TargetSG.channel_add)
async def tgt_ch_add_save(message: Message, state: FSMContext):
    val = (message.text or "").strip()
    if not val:
        await message.answer("❌ မှန်တဲ့ username ပို့ပါ။")
        return

    async with async_session() as db:
        await add_channel(db, message.from_user.id, val)
    await state.clear()
    await message.answer(f"✅ <code>{val}</code> ထည့်ပြီး")
    await _render_targets(message)
