"""Keyboards pentru grupuri."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.main_menu import back_btn


def my_groups_kb(groups: list) -> InlineKeyboardMarkup:
    rows = []
    for g in groups:
        rows.append([
            InlineKeyboardButton(f"👥 {g['name']}", callback_data=f"g_view_{g['id']}")
        ])
    rows.append([
        InlineKeyboardButton("➕ Creează grup", callback_data="cg"),
        InlineKeyboardButton("🔗 Alătură-te",   callback_data="jg"),
    ])
    rows.append([back_btn()])
    return InlineKeyboardMarkup(rows)


def group_list_kb(items: list, group_id: int) -> InlineKeyboardMarkup:
    """Lista produselor unui grup cu butoane toggle + delete."""
    rows = []
    for item in items:
        icon  = "✅" if item["checked"] else "⬜"
        name  = item["item"]
        label = f"{icon} {name}" if len(name) <= 22 else f"{icon} {name[:20]}…"
        qty   = f" ×{item['quantity']}" if item["quantity"] != "1" else ""
        rows.append([
            InlineKeyboardButton(label + qty,     callback_data=f"g_chk_{item['id']}_{group_id}"),
            InlineKeyboardButton("🗑",              callback_data=f"g_del_{item['id']}_{group_id}"),
        ])
    rows.append([
        InlineKeyboardButton("➕ Adaugă",      callback_data=f"g_add_{group_id}"),
        InlineKeyboardButton("🧹 Șterge bifate", callback_data=f"g_clr_{group_id}"),
    ])
    rows.append([
        InlineKeyboardButton("👥 Membri",       callback_data=f"g_mem_{group_id}"),
        InlineKeyboardButton("🚪 Ieși",          callback_data=f"g_leave_{group_id}"),
    ])
    rows.append([back_btn()])
    return InlineKeyboardMarkup(rows)


def group_empty_kb(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Adaugă primul produs", callback_data=f"g_add_{group_id}")],
        [InlineKeyboardButton("👥 Membri", callback_data=f"g_mem_{group_id}")],
        [InlineKeyboardButton("🚪 Ieși din grup",        callback_data=f"g_leave_{group_id}")],
        [back_btn()],
    ])


def group_cancel_kb(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Anulează", callback_data=f"g_view_{group_id}")],
    ])


def members_kb(members: list, group_id: int, owner_id: int, viewer_id: int) -> InlineKeyboardMarkup:
    """Afișează membrii. Ownerul vede butoane de kick."""
    rows = []
    for m in members:
        name = m["first_name"] or m["username"] or f"User #{m['user_id']}"
        crown = " 👑" if m["user_id"] == owner_id else ""
        if viewer_id == owner_id and m["user_id"] != owner_id:
            rows.append([
                InlineKeyboardButton(f"{name}{crown}", callback_data="noop"),
                InlineKeyboardButton("❌ Elimină",      callback_data=f"g_kick_{group_id}_{m['user_id']}"),
            ])
        else:
            rows.append([InlineKeyboardButton(f"{name}{crown}", callback_data="noop")])
    rows.append([InlineKeyboardButton("◀️ Înapoi la listă", callback_data=f"g_view_{group_id}")])
    rows.append([back_btn()])
    return InlineKeyboardMarkup(rows)


def edit_groups_kb(groups: list) -> InlineKeyboardMarkup:
    """Lista grupurilor pe care userul le deține (poate edita)."""
    rows = []
    for g in groups:
        rows.append([
            InlineKeyboardButton(f"⚙️ {g['name']}", callback_data=f"g_edit_{g['id']}")
        ])
    if not groups:
        rows.append([InlineKeyboardButton("Nu ești owner la niciun grup", callback_data="noop")])
    rows.append([back_btn()])
    return InlineKeyboardMarkup(rows)


def group_edit_kb(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Redenumește grupul",   callback_data=f"g_rename_{group_id}")],
        [InlineKeyboardButton("👥 Gestionează membri",    callback_data=f"g_mem_{group_id}")],
        [InlineKeyboardButton("🔗 Cod invitație",          callback_data=f"g_code_{group_id}")],
        [InlineKeyboardButton("🗑 Șterge grupul",          callback_data=f"g_del_group_{group_id}")],
        [InlineKeyboardButton("◀️ Înapoi la grup",         callback_data=f"g_view_{group_id}")],
        [back_btn()],
    ])


def confirm_delete_group_kb(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Da, șterge",  callback_data=f"g_del_group_yes_{group_id}"),
            InlineKeyboardButton("❌ Anulează",     callback_data=f"g_edit_{group_id}"),
        ]
    ])


def confirm_leave_kb(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Da, ieși",  callback_data=f"g_leave_yes_{group_id}"),
            InlineKeyboardButton("❌ Rămâi",     callback_data=f"g_view_{group_id}"),
        ]
    ])


def join_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Anulează", callback_data="mg")],
    ])


def create_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Anulează", callback_data="mg")],
    ])


def rename_cancel_kb(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Anulează", callback_data=f"g_edit_{group_id}")],
    ])
