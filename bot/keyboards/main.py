from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Sessions"), KeyboardButton(text="🎯 Targets")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="⏱️ Timer")],
            [KeyboardButton(text="📊 Status"), KeyboardButton(text="🎛️ Services")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Menu ကို သုံးပါ 👇",
    )
    return keyboard
