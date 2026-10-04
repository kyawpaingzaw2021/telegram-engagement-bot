from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main import main_menu
from bot.keyboards.inline import back_button

router = Router()


WELCOME = (
    "🤖 <b>Telegram Engagement Bot</b>\n\n"
    "အောက်က menu ကနေ စတင်ပါ —\n\n"
    "⚙️ <b>Settings</b> — API + Task settings\n"
    "📱 <b>Sessions</b> — Account ထည့်/ထုတ်\n"
    "🎯 <b>Targets</b> — Bot / Channels / Ads\n"
    "⏱️ <b>Timer</b> — On/Off\n"
    "📊 <b>Status</b> — Progress\n"
    "🎛️ <b>Services</b> — Engine control\n"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_menu())


@router.message(F.text == "❓ Help")
async def help_reply(message: Message):
    await message.answer(
        "❓ <b>Help</b>\n\n"
        "Settings ထဲက Help ကို နှိပ်ပါ။",
        reply_markup=main_menu(),
    )


@router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(WELCOME, reply_markup=back_button())
    await call.answer()


@router.callback_query(F.data == "cancel")
async def cancel_cb(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Cancelled.", reply_markup=None)
    await call.answer()
