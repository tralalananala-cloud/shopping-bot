"""Keyboard meniu principal și helper buton 🏠."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def back_btn() -> InlineKeyboardButton:
    """Buton reutilizabil '🏠 Meniu principal' — inclus pe TOATE paginile."""
    return InlineKeyboardButton("🏠 Meniu principal", callback_data="mm")


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Lista mea personală", callback_data="pl")],
        [InlineKeyboardButton("👥 Grupurile mele",      callback_data="mg")],
        [
            InlineKeyboardButton("➕ Creează grup",       callback_data="cg"),
            InlineKeyboardButton("🔗 Alătură-te",         callback_data="jg"),
        ],
        [InlineKeyboardButton("⚙️ Editează grupuri",    callback_data="eg")],
        [InlineKeyboardButton("ℹ️ Ajutor",              callback_data="help")],
    ])
