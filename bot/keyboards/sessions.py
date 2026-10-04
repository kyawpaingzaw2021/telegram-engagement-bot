from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def sessions_menu(sessions: list) -> InlineKeyboardMarkup:
    rows = []
    for s in sessions:
        emoji = "🟢" if s.status == "active" else "🟡" if s.status == "error" else "🔴"
        label = f"{emoji} {s.label} — {s.phone}"
        rows.append([
            InlineKeyboardButton(text=label, callback_data=f"sess_view:{s.id}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"sess_del:{s.id}"),
        ])

    rows.append([
        InlineKeyboardButton(text="➕ Add Session", callback_data="sess_add"),
        InlineKeyboardButton(text="🔄 Refresh", callback_data="sess_refresh"),
    ])
    rows.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def session_view_kb(session_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑️ Remove", callback_data=f"sess_del:{session_id}"
                ),
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="sess_refresh")],
        ]
    )


def confirm_delete_kb(session_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Yes, Remove", callback_data=f"sess_del_confirm:{session_id}"
                ),
                InlineKeyboardButton(text="❌ Cancel", callback_data="sess_refresh"),
            ]
        ]
    )
