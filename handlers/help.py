"""Handler pentru ℹ️ Ajutor."""

from telegram import Update
from telegram.ext import ContextTypes
from keyboards.main_menu import main_menu_kb


HELP_TEXT = (
    "ℹ️ <b>Ajutor — BotListă Multi-User</b>\n\n"

    "<b>📝 Lista mea personală</b>\n"
    "• Vizualizează și gestionează produsele tale private\n"
    "• Apasă pe produs pentru a-l bifa/debifa\n"
    "• 🗑 șterge produsul definitiv\n"
    "• 📤 Partajează lista într-un grup\n\n"

    "<b>👥 Grupuri</b>\n"
    "• Creează un grup și invită familia/prietenii\n"
    "• Alătură-te cu un cod de 6 caractere\n"
    "• Lista grupului e vizibilă tuturor membrilor\n"
    "• Fiecare produs arată cine l-a adăugat\n\n"

    "<b>⚙️ Editare grup (doar owner)</b>\n"
    "• Redenumește grupul\n"
    "• Elimină membri\n"
    "• Șterge grupul\n\n"

    "<b>💡 Sfat adăugare produse</b>\n"
    "Poți include cantitatea:\n"
    "<code>lapte 2</code>  →  lapte ×2\n\n"

    "<b>🔗 Partajare</b>\n"
    "Trimite codul de invitație sau link-ul direct prietenilor."
)


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        HELP_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
