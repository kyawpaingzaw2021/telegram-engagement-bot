from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import cancel_kb
from bot.keyboards.settings import settings_menu, choice_kb, help_kb
from bot.states.session_states import SettingsSG
from db.repo.users import get_user, update_user
from db.session import async_session

router = Router()


SETTINGS_TITLE = "⚙️ <b>Settings</b>\n\nချိန်ညှိလိုတာ ရွေးပါ —"


HELP_TEXT = (
    "❓ <b>Help</b>\n\n"
    "<b>အသုံးပြုနည်း</b>\n"
    "1️⃣ Settings → API ID/Hash ထည့်ပါ\n"
    "2️⃣ Sessions → Add Session (phone + OTP)\n"
    "3️⃣ Targets → Bot / Channels / Ads ထည့်ပါ\n"
    "4️⃣ Settings → View/React/Ads/Delay သတ်မှတ်\n"
    "5️⃣ Timer → 🟢 ON\n"
    "6️⃣ Status → Progress ကြည့်\n\n"
    "<b>⚠️ သတိထားရန်</b>\n"
    "• Session 1 = Account 1\n"
    "• React အတွက် Premium account လိုအပ်\n"
    "• FloodWait ဖြစ်ရင် auto wait\n"
    "• Dead session auto remove\n"
)


async def _render_settings(call: CallbackQuery):
    async with async_session() as db:
        user = await get_user(db, call.from_user.id)
        if user is None:
            await call.message.edit_text("⚠️ User မတွေ့။ /start ပြန်ပို့ပါ။")
            return
        await call.message.edit_text(
            SETTINGS_TITLE,
            reply_markup=settings_menu(user),
        )


@router.message(F.text == "⚙️ Settings")
async def open_settings(message: Message):
    async with async_session() as db:
        user = await get_user(db, message.from_user.id)
        if user is None:
            await message.answer("⚠️ /start ကို အရင်ပို့ပါ။")
            return
        await message.answer(
            SETTINGS_TITLE,
            reply_markup=settings_menu(user),
        )


@router.callback_query(F.data == "back_settings")
async def back_settings(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await _render_settings(call)
    await call.answer()


# ---------- API ID ----------
@router.callback_query(F.data == "set_api_id")
async def set_api_id_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsSG.api_id)
    await call.message.edit_text(
        "🔑 <b>API ID</b> ပို့ပါ\n\n"
        "my.telegram.org → API development tools ကနေ ယူပါ။\n"
        "ဥပမာ — <code>1234567</code>",
        reply_markup=cancel_kb("back_settings"),
    )
    await call.answer()


@router.message(SettingsSG.api_id)
async def set_api_id_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("❌ ဂဏန်းပဲ ပို့ပါ။ ပြန်စမ်းပါ:")
        return

    async with async_session() as db:
        await update_user(db, message.from_user.id, api_id=int(text))
        user = await get_user(db, message.from_user.id)

    await state.clear()
    await message.answer(
        f"✅ API ID သိမ်းပြီး: <code>{user.api_id}</code>",
        reply_markup=settings_menu(user),
    )


# ---------- API Hash ----------
@router.callback_query(F.data == "set_api_hash")
async def set_api_hash_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsSG.api_hash)
    await call.message.edit_text(
        "🔑 <b>API HASH</b> ပို့ပါ\n\n"
        "my.telegram.org ကနေ ယူပါ။\n"
        "ဥပမာ — <code>abcdef1234567890...</code>",
        reply_markup=cancel_kb("back_settings"),
    )
    await call.answer()


@router.message(SettingsSG.api_hash)
async def set_api_hash_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if len(text) < 10:
        await message.answer("❌ API Hash မမှန်ဘူး။ ပြန်ပို့ပါ:")
        return

    async with async_session() as db:
        await update_user(db, message.from_user.id, api_hash=text)
        user = await get_user(db, message.from_user.id)

    await state.clear()
    await message.answer(
        "✅ API Hash သိမ်းပြီး",
        reply_markup=settings_menu(user),
    )


# ---------- View ----------
@router.callback_query(F.data == "set_view")
async def set_view(call: CallbackQuery):
    await call.message.edit_text(
        "👁️ <b>View count</b> ရွေးပါ",
        reply_markup=choice_kb("view", [10, 20, 30]),
    )
    await call.answer()


@router.callback_query(F.data.startswith("view:"))
async def set_view_save(call: CallbackQuery):
    value = int(call.data.split(":")[1])
    async with async_session() as db:
        await update_user(db, call.from_user.id, view_count=value)
        user = await get_user(db, call.from_user.id)
    await call.message.edit_text(
        f"✅ View = <b>{value}</b>",
        reply_markup=settings_menu(user),
    )
    await call.answer()


# ---------- React ----------
@router.callback_query(F.data == "set_react")
async def set_react(call: CallbackQuery):
    await call.message.edit_text(
        "❤️ <b>React count</b> ရွေးပါ",
        reply_markup=choice_kb("react", [10, 15, 20]),
    )
    await call.answer()


@router.callback_query(F.data.startswith("react:"))
async def set_react_save(call: CallbackQuery):
    value = int(call.data.split(":")[1])
    async with async_session() as db:
        await update_user(db, call.from_user.id, react_count=value)
        user = await get_user(db, call.from_user.id)
    await call.message.edit_text(
        f"✅ React = <b>{value}</b>",
        reply_markup=settings_menu(user),
    )
    await call.answer()


# ---------- Ads ----------
@router.callback_query(F.data == "set_ads")
async def set_ads(call: CallbackQuery):
    await call.message.edit_text(
        "📺 <b>Ads count</b> ရွေးပါ",
        reply_markup=choice_kb("ads", [3, 5, 10]),
    )
    await call.answer()


@router.callback_query(F.data.startswith("ads:"))
async def set_ads_save(call: CallbackQuery):
    value = int(call.data.split(":")[1])
    async with async_session() as db:
        await update_user(db, call.from_user.id, ads_count=value)
        user = await get_user(db, call.from_user.id)
    await call.message.edit_text(
        f"✅ Ads = <b>{value}</b>",
        reply_markup=settings_menu(user),
    )
    await call.answer()


# ---------- Delay ----------
@router.callback_query(F.data == "set_delay")
async def set_delay(call: CallbackQuery):
    await call.message.edit_text(
        "⏱️ <b>Delay (minutes)</b> ရွေးပါ",
        reply_markup=choice_kb("delay", [5, 10, 15]),
    )
    await call.answer()


@router.callback_query(F.data.startswith("delay:"))
async def set_delay_save(call: CallbackQuery):
    value = int(call.data.split(":")[1])
    async with async_session() as db:
        await update_user(db, call.from_user.id, delay_minutes=value)
        user = await get_user(db, call.from_user.id)
    await call.message.edit_text(
        f"✅ Delay = <b>{value}m</b>",
        reply_markup=settings_menu(user),
    )
    await call.answer()


# ---------- Help ----------
@router.callback_query(F.data == "help")
async def show_help(call: CallbackQuery):
    await call.message.edit_text(HELP_TEXT, reply_markup=help_kb())
    await call.answer()
