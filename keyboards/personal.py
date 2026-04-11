"""Keyboards pentru lista personală."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.main_menu import back_btn


def personal_list_kb(items: list) -> InlineKeyboardMarkup:
    """Un buton per produs (toggle checked) + 🗑 delete, plus acțiuni globale."""
    rows = []
    for item in items:
        icon  = "✅" if item["checked"] else "⬜"
        name  = item["item"]
        label = f"{icon} {name}" if len(name) <= 22 else f"{icon} {name[:20]}…"
        qty   = f" ×{item['quantity']}" if item["quantity"] != "1" else ""
        rows.append([
            InlineKeyboardButton(label + qty, callback_data=f"pl_chk_{item['id']}"),
            InlineKeyboardButton("🗑",         callback_data=f"pl_del_{item['id']}"),
        ])

    rows.append([
        InlineKeyboardButton("➕ Adaugă produs", callback_data="pl_add"),
        InlineKeyboardButton("🧹 Șterge bifate", callback_data="pl_clr"),
    ])
    rows.append([
        InlineKeyboardButton("📤 Partajează în grup", callback_data="pl_share"),
        back_btn(),
    ])
    return InlineKeyboardMarkup(rows)


def personal_empty_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Adaugă primul produs", callback_data="pl_add")],
        [back_btn()],
    ])


def personal_cancel_kb() -> InlineKeyboardMarkup:
    """Keyboard afișat când așteptăm input text — doar buton anulare."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Anulează", callback_data="pl")],
    ])


def share_groups_kb(groups: list) -> InlineKeyboardMarkup:
    """Alege grupul în care să partajezi lista personală."""
    rows = []
    for g in groups:
        rows.append([
            InlineKeyboardButton(
                f"👥 {g['name']}", callback_data=f"pl_share_g_{g['id']}"
            )
        ])
    rows.append([back_btn()])
    return InlineKeyboardMarkup(rows)
