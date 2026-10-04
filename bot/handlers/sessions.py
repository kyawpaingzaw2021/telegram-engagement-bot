from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from telethon.errors import (
    AuthKeyUnregisteredError,
    SessionRevokedError,
    UserDeactivatedError,
)

from bot.keyboards.inline import cancel_kb
from bot.keyboards.sessions import (
    confirm_delete_kb,
    session_view_kb,
    sessions_menu,
)
from bot.states.session_states import AddSessionSG
from core import temp_state
from core.session_manager import make_temp_client
from db.repo.sessions import (
    create_session,
    delete_session,
    get_session_by_id,
    get_sessions,
)
from db.repo.users import get_user
from db.session import async_session

router = Router()


async def _render_sessions(message_or_call, user_id: int):
    async with async_session() as db:
        sessions = await get_sessions(db, user_id)

    text = f"📱 <b>Sessions</b> ({len(sessions)})\n\n"
    if not sessions:
        text += "ဘာ session မှ မရှိသေးဘူး။ ➕ Add Session နှိပ်ပါ။"
    else:
        for i, s in enumerate(sessions, 1):
            emoji = "🟢" if s.status == "active" else "🟡" if s.status == "error" else "🔴"
            text += f"{i}. {emoji} <b>{s.label}</b> — {s.phone}\n"

    kb = sessions_menu(sessions)
    if isinstance(message_or_call, CallbackQuery):
        try:
            await message_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await message_or_call.message.answer(text, reply_markup=kb)
    else:
        await message_or_call.answer(text, reply_markup=kb)


@router.message(F.text == "📱 Sessions")
async def open_sessions(message: Message, state: FSMContext):
    await state.clear()
    await _render_sessions(message, message.from_user.id)


@router.callback_query(F.data == "sess_refresh")
async def refresh_sessions(call: CallbackQuery):
    await _render_sessions(call, call.from_user.id)
    await call.answer()


# ---------- Add Session ----------
@router.callback_query(F.data == "sess_add")
async def add_session_start(call: CallbackQuery, state: FSMContext):
    async with async_session() as db:
        user = await get_user(db, call.from_user.id)

    if not user or not user.api_id or not user.api_hash:
        await call.message.edit_text(
            "⚠️ <b>API မရှိသေး</b>\n\n"
            "⚙️ Settings → API ID/Hash အရင် ထည့်ပါ။",
            reply_markup=cancel_kb("back_main"),
        )
        await call.answer()
        return

    await state.set_state(AddSessionSG.phone)
    await call.message.edit_text(
        "📱 <b>Phone number</b> ပို့ပါ\n\n"
        "Format: <code>+959xxxxxxxxx</code>",
        reply_markup=cancel_kb("cancel"),
    )
    await call.answer()


@router.message(AddSessionSG.phone)
async def add_session_phone(message: Message, state: FSMContext):
    phone = (message.text or "").strip()
    if not phone.startswith("+") or len(phone) < 8:
        await message.answer("❌ Format မှန် မဟုတ်ဘူး။ ဥပမာ — <code>+959789466123</code>")
        return

    async with async_session() as db:
        user = await get_user(db, message.from_user.id)

    try:
        client = make_temp_client(user.api_id, user.api_hash)
        await client.connect()
        sent = await client.send_code_request(phone)

        temp_state.temp_clients[message.from_user.id] = client
        temp_state.temp_phones[message.from_user.id] = phone
        temp_state.temp_api[message.from_user.id] = (user.api_id, user.api_hash)
        temp_state.temp_code_hash[message.from_user.id] = sent.phone_code_hash

        await state.set_state(AddSessionSG.otp)
        await message.answer(
            "📨 <b>OTP</b> ပို့ပါ (5 min အတွင်း)\n\n"
            "Telegram မှာ ရောက်တဲ့ code ကို ရိုက်ထည့်ပါ။",
            reply_markup=cancel_kb("cancel"),
        )
    except Exception as e:
        temp_state.clear(message.from_user.id)
        await state.clear()
        await message.answer(f"❌ Error: <code>{e}</code>\n\nပြန်စမ်းပါ။")


@router.message(AddSessionSG.otp)
async def add_session_otp(message: Message, state: FSMContext):
    code = (message.text or "").strip()
    uid = message.from_user.id

    client = temp_state.get_temp_client(uid)
    phone = temp_state.get_temp_phone(uid)
    code_hash = temp_state.get_code_hash(uid)

    if not client or not phone or not code_hash:
        await state.clear()
        await message.answer("❌ Session ပျောက်သွားပြီ။ ပြန်စပါ။")
        return

    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
    except Exception as e:
        err_name = type(e).__name__
        if "SessionPasswordNeeded" in err_name:
            await state.set_state(AddSessionSG.password)
            await message.answer(
                "🔐 <b>2FA password</b> ပို့ပါ\n\n"
                "မရှိရင် [⏭️ Skip] နှိပ်။",
                reply_markup=cancel_kb("cancel"),
            )
            return
        else:
            temp_state.clear(uid)
            await state.clear()
            await message.answer(f"❌ OTP error: <code>{e}</code>")
            return

    # Success — no 2FA
    await _finalize_session(message, state, uid)


@router.message(AddSessionSG.password)
async def add_session_password(message: Message, state: FSMContext):
    uid = message.from_user.id
    pwd = (message.text or "").strip()

    client = temp_state.get_temp_client(uid)
    if not client:
        await state.clear()
        await message.answer("❌ Session ပျောက်သွားပြီ။")
        return

    try:
        await client.sign_in(password=pwd)
    except Exception as e:
        await message.answer(f"❌ Password error: <code>{e}</code>")
        return

    await _finalize_session(message, state, uid)


async def _finalize_session(message: Message, state: FSMContext, uid: int):
    client = temp_state.get_temp_client(uid)
    try:
        session_string = client.session.save()
        phone = temp_state.get_temp_phone(uid)
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        temp_state.clear(uid)

    await state.update_data(session_string=session_string, phone=phone)
    await state.set_state(AddSessionSG.label)
    await message.answer(
        "✅ <b>Session ဖန်တီးပြီး!</b>\n\n"
        "Label ပေးပါ (ဥပမာ — <code>acc1</code>)",
        reply_markup=cancel_kb("cancel"),
    )


@router.message(AddSessionSG.label)
async def add_session_label(message: Message, state: FSMContext):
    label = (message.text or "").strip()
    if not label or len(label) > 32:
        await message.answer("❌ Label 1-32 char ပါရမယ်။")
        return

    data = await state.get_data()
    session_string = data.get("session_string")
    phone = data.get("phone")

    if not session_string:
        await state.clear()
        await message.answer("❌ Session data ပျောက်။ ပြန်စပါ။")
        return

    async with async_session() as db:
        await create_session(
            db,
            user_id=message.from_user.id,
            label=label,
            phone=phone,
            session_string=session_string,
        )

    await state.clear()
    await message.answer(
        f"✅ <b>{label}</b> သိမ်းပြီးပါပြီ။",
        reply_markup=None,
    )
    await _render_sessions(message, message.from_user.id)


# ---------- Session View / Delete ----------
@router.callback_query(F.data.startswith("sess_view:"))
async def view_session(call: CallbackQuery):
    sid = int(call.data.split(":")[1])
    async with async_session() as db:
        s = await get_session_by_id(db, sid)
    if not s:
        await call.answer("မတွေ့ဘူး", show_alert=True)
        return

    text = (
        f"📱 <b>{s.label}</b>\n\n"
        f"📞 {s.phone}\n"
        f"📊 Status: {s.status}\n"
        f"🕒 Last run: {s.last_run_at or '—'}\n"
        f"⚠️ Error: {s.last_error or '—'}\n"
    )
    await call.message.edit_text(text, reply_markup=session_view_kb(sid))
    await call.answer()


@router.callback_query(F.data.startswith("sess_del:"))
async def delete_session_ask(call: CallbackQuery):
    sid = int(call.data.split(":")[1])
    await call.message.edit_text(
        "⚠️ <b>Session ထုတ်မှာ သေချာလား?</b>\n\n"
        "Account က Telegram device list ကနေ log out ဖြစ်မယ်။",
        reply_markup=confirm_delete_kb(sid),
    )
    await call.answer()


@router.callback_query(F.data.startswith("sess_del_confirm:"))
async def delete_session_do(call: CallbackQuery):
    sid = int(call.data.split(":")[1])

    async with async_session() as db:
        s = await get_session_by_id(db, sid)
        if not s:
            await call.answer("မတွေ့ဘူး", show_alert=True)
            return

        # Log out from Telegram
        try:
            from core.session_manager import make_client
            async with async_session() as db2:
                user = await get_user(db2, s.user_id)
            client = make_client(s.session_string, user.api_id, user.api_hash)
            await client.connect()
            await client.log_out()
            await client.disconnect()
        except Exception:
            pass

        await delete_session(db, sid)

    await call.message.edit_text("✅ Session ထုတ်ပြီး။")
    await call.answer()
    await _render_sessions(call, call.from_user.id)
