from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def settings_menu(user) -> InlineKeyboardMarkup:
    api_id_text = str(user.api_id) if user.api_id else "—"
    api_hash_text = "•••••••" if user.api_hash else "—"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🔑 API ID: {api_id_text}",
                    callback_data="set_api_id",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"🔑 API Hash: {api_hash_text}",
                    callback_data="set_api_hash",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"👁️ View: {user.view_count}",
                    callback_data="set_view",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"❤️ React: {user.react_count}",
                    callback_data="set_react",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"📺 Ads: {user.ads_count}",
                    callback_data="set_ads",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"⏱️ Delay: {user.delay_minutes}m",
                    callback_data="set_delay",
                ),
            ],
            [
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
                InlineKeyboardButton(text="⬅️ Back", callback_data="back_main"),
            ],
        ]
    )
    return kb


def choice_kb(prefix: str, options: list, back: str = "back_settings") -> InlineKeyboardMarkup:
    rows = []
    row = []
    for opt in options:
        row.append(
            InlineKeyboardButton(
                text=str(opt),
                callback_data=f"{prefix}:{opt}",
            )
        )
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="⬅️ Back", callback_data=back)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_settings")]
        ]
    )
