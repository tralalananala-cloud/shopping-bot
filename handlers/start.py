"""Handler /start și meniu principal."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database.users import ensure_user
from utils.helpers import go_to_main_menu, send_main_menu, log_action

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Înregistrează userul și afișează meniul principal."""
    user = update.effective_user
    await ensure_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )
    log_action(user.id, "/start")

    # Suport deep-link: /start join_ABCDEF
    if context.args and context.args[0].startswith("join_"):
        code = context.args[0][5:]
        context.user_data["pending_join_code"] = code
        await send_main_menu(update, context)
        await update.message.reply_text(
            f"🔗 Cod de invitație detectat: <code>{code}</code>\n"
            "Apasă <b>🔗 Alătură-te unui grup</b> pentru a continua.",
            parse_mode="HTML",
        )
        return

    await send_main_menu(update, context)


async def cb_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback pentru butonul '🏠 Meniu principal' de pe orice ecran."""
    await update.callback_query.answer()
    await go_to_main_menu(update.callback_query)
