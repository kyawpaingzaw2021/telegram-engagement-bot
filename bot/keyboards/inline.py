from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_button(callback: str = "back_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data=callback)]]
    )


def confirm_kb(yes_data: str, no_data: str = "back_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes", callback_data=yes_data),
                InlineKeyboardButton(text="❌ Cancel", callback_data=no_data),
            ]
        ]
    )


def cancel_kb(cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data=cancel_data)]
        ]
    )
