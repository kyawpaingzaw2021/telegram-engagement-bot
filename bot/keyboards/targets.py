from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


PAGE_SIZE = 5


def targets_menu(target, channels_count: int) -> InlineKeyboardMarkup:
    bot_text = target.target_bot or "—"
    ads_text = target.ads_channel or "—"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🤖 Bot: {bot_text}", callback_data="tgt_bot")],
            [InlineKeyboardButton(text=f"📢 Channels: {channels_count}", callback_data="tgt_ch_list:0")],
            [InlineKeyboardButton(text=f"📺 Ads: {ads_text}", callback_data="tgt_ads")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")],
        ]
    )


def single_field_kb(field: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Change", callback_data=f"tgt_change:{field}"),
                InlineKeyboardButton(text="🗑️ Remove", callback_data=f"tgt_remove:{field}"),
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="tgt_back")],
        ]
    )


def channels_list_kb(channels: list, page: int) -> InlineKeyboardMarkup:
    total = len(channels)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = channels[start:end]

    rows = []
    for ch in page_items:
        emoji = "🟢" if ch.is_active else "🔴"
        rows.append([
            InlineKeyboardButton(
                text=f"{emoji} {ch.channel_username}",
                callback_data=f"tgt_ch_toggle:{ch.id}:{page}",
            ),
            InlineKeyboardButton(text="🗑️", callback_data=f"tgt_ch_del:{ch.id}:{page}"),
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"tgt_ch_list:{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"tgt_ch_list:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([
        InlineKeyboardButton(text="➕ Add", callback_data="tgt_ch_add"),
        InlineKeyboardButton(text="⬅️ Back", callback_data="tgt_back"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
