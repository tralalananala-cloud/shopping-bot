"""
Punct de intrare principal — configurare Application și înregistrare handleri.
"""

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database.db import init_db
from handlers.start    import cmd_start, cb_main_menu
from handlers.personal import (
    show_personal_list,
    start_add_item,
    receive_add_item,
    toggle_item,
    delete_item,
    clear_checked,
    share_list_select,
    share_list_execute,
    cancel_personal,
)
from handlers.groups import (
    show_my_groups,
    show_group,
    show_members,
    start_add_group_item,
    receive_add_group_item,
    toggle_group_item,
    delete_group_item,
    clear_group_checked,
    show_invite_code,
    start_create_group,
    receive_group_name,
    start_join_group,
    receive_join_code,
    confirm_leave,
    execute_leave,
    cancel_groups,
)
from handlers.admin import (
    show_edit_groups,
    show_group_edit,
    start_rename_group,
    receive_rename_group,
    kick_member,
    confirm_delete_group,
    execute_delete_group,
    cancel_admin,
)
from handlers.help import show_help
from utils.states import (
    PERSONAL_ADD_ITEM,
    GROUP_CREATE_NAME,
    GROUP_JOIN_CODE,
    GROUP_ADD_ITEM,
    GROUP_RENAME,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_conversation_handler() -> ConversationHandler:
    """
    Un singur ConversationHandler acoperă toate fluxurile multi-pas:
    - adăugare produs personal
    - creare grup
    - alăturare grup
    - adăugare produs în grup
    - redenumire grup
    """
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_item,        pattern=r"^pl_add$"),
            CallbackQueryHandler(start_create_group,    pattern=r"^cg$"),
            CallbackQueryHandler(start_join_group,      pattern=r"^jg$"),
            CallbackQueryHandler(start_add_group_item,  pattern=r"^g_add_\d+$"),
            CallbackQueryHandler(start_rename_group,    pattern=r"^g_rename_\d+$"),
        ],
        states={
            PERSONAL_ADD_ITEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_item),
            ],
            GROUP_CREATE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_group_name),
            ],
            GROUP_JOIN_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_join_code),
            ],
            GROUP_ADD_ITEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_group_item),
            ],
            GROUP_RENAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rename_group),
            ],
        },
        fallbacks=[
            CommandHandler("start",              cmd_start),
            CallbackQueryHandler(cancel_personal, pattern=r"^pl$"),
            CallbackQueryHandler(cancel_groups,   pattern=r"^mg$"),
            CallbackQueryHandler(cancel_admin,    pattern=r"^eg$"),
            CallbackQueryHandler(cb_main_menu,    pattern=r"^mm$"),
        ],
        per_message=False,
        allow_reentry=True,
    )


async def post_init(application: Application) -> None:
    """Inițializare DB la pornirea aplicației."""
    logger.info("Inițializare bază de date...")
    await init_db()
    logger.info("DB gata.")


def main() -> None:
    logger.info("Pornire BotListă Multi-User...")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── ConversationHandler (FSM) — prioritate maximă
    app.add_handler(build_conversation_handler())

    # ── Comenzi
    app.add_handler(CommandHandler("start", cmd_start))

    # ── Meniu principal
    app.add_handler(CallbackQueryHandler(cb_main_menu,       pattern=r"^mm$"))
    app.add_handler(CallbackQueryHandler(show_help,          pattern=r"^help$"))

    # ── Lista personală
    app.add_handler(CallbackQueryHandler(show_personal_list, pattern=r"^pl$"))
    app.add_handler(CallbackQueryHandler(toggle_item,        pattern=r"^pl_chk_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_item,        pattern=r"^pl_del_\d+$"))
    app.add_handler(CallbackQueryHandler(clear_checked,      pattern=r"^pl_clr$"))
    app.add_handler(CallbackQueryHandler(share_list_select,  pattern=r"^pl_share$"))
    app.add_handler(CallbackQueryHandler(share_list_execute, pattern=r"^pl_share_g_\d+$"))

    # ── Grupuri — vizualizare
    app.add_handler(CallbackQueryHandler(show_my_groups,     pattern=r"^mg$"))
    app.add_handler(CallbackQueryHandler(show_group,         pattern=r"^g_view_\d+$"))
    app.add_handler(CallbackQueryHandler(show_members,       pattern=r"^g_mem_\d+$"))
    app.add_handler(CallbackQueryHandler(show_invite_code,   pattern=r"^g_code_\d+$"))

    # ── Grupuri — produse
    app.add_handler(CallbackQueryHandler(toggle_group_item,  pattern=r"^g_chk_\d+_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_group_item,  pattern=r"^g_del_\d+_\d+$"))
    app.add_handler(CallbackQueryHandler(clear_group_checked,pattern=r"^g_clr_\d+$"))

    # ── Grupuri — ieșire
    app.add_handler(CallbackQueryHandler(confirm_leave,      pattern=r"^g_leave_\d+$"))
    app.add_handler(CallbackQueryHandler(execute_leave,      pattern=r"^g_leave_yes_\d+$"))

    # ── Admin grup
    app.add_handler(CallbackQueryHandler(show_edit_groups,       pattern=r"^eg$"))
    app.add_handler(CallbackQueryHandler(show_group_edit,        pattern=r"^g_edit_\d+$"))
    app.add_handler(CallbackQueryHandler(kick_member,            pattern=r"^g_kick_\d+_\d+$"))
    app.add_handler(CallbackQueryHandler(confirm_delete_group,   pattern=r"^g_del_group_\d+$"))
    app.add_handler(CallbackQueryHandler(execute_delete_group,   pattern=r"^g_del_group_yes_\d+$"))

    # ── Buton fără acțiune (etichete de afișare)
    app.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern=r"^noop$"))

    logger.info("Botul rulează. Ctrl+C pentru oprire.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
