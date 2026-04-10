"""
Punct de intrare principal pentru botul de cumpărături Telegram.
Rulare: python bot.py
"""

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from handlers import (
    cmd_add,
    cmd_clear,
    cmd_done,
    cmd_help,
    cmd_invite,
    cmd_join,
    cmd_leave,
    cmd_list,
    cmd_members,
    cmd_remove,
    cmd_share,
    cmd_start,
    cmd_undo,
    handle_callback,
    handle_text,
)

# ---------------------------------------------------------------------------
# Configurare logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Construiește aplicația și pornește polling-ul."""
    logger.info("Pornire bot lista de cumpărături...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Înregistrare handleri de comenzi
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CommandHandler("remove", cmd_remove))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("undo", cmd_undo))
    app.add_handler(CommandHandler("share", cmd_share))
    app.add_handler(CommandHandler("invite", cmd_invite))
    app.add_handler(CommandHandler("join", cmd_join))
    app.add_handler(CommandHandler("leave", cmd_leave))
    app.add_handler(CommandHandler("members", cmd_members))

    # Handler pentru butoane inline
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Handler pentru mesaje text libere (orice text care nu e comandă)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Botul rulează. Apasă Ctrl+C pentru a opri.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
