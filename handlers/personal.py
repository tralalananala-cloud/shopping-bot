"""
Handlers pentru lista personală.
Fluxuri FSM: adăugare produs (PERSONAL_ADD_ITEM).
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import database.personal as db_personal
import database.groups as db_groups
from keyboards.personal import (
    personal_list_kb,
    personal_empty_kb,
    personal_cancel_kb,
    share_groups_kb,
)
from keyboards.main_menu import back_btn
from utils.helpers import (
    format_personal_list,
    go_to_main_menu_end,
    parse_item_input,
    log_action,
    esc,
)
from utils.states import PERSONAL_ADD_ITEM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Vizualizare listă personală
# ---------------------------------------------------------------------------

async def show_personal_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    items = await db_personal.get_items(user_id)
    text  = format_personal_list(items)
    kb    = personal_list_kb(items) if items else personal_empty_kb()

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    log_action(user_id, "view personal list", f"{len(items)} items")


# ---------------------------------------------------------------------------
# Adăugare produs — FSM
# ---------------------------------------------------------------------------

async def start_add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Intrare în FSM: așteptăm textul produsului."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "✏️ <b>Adaugă produs</b>\n\n"
        "Scrie numele produsului (opțional cantitatea după spațiu):\n"
        "<code>lapte</code>  sau  <code>lapte 2</code>",
        parse_mode="HTML",
        reply_markup=personal_cancel_kb(),
    )
    return PERSONAL_ADD_ITEM


async def receive_add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Primim textul produsului, îl adăugăm și arătăm lista actualizată."""
    user_id = update.effective_user.id
    text    = update.message.text.strip()

    if not text:
        await update.message.reply_text("❌ Textul nu poate fi gol. Încearcă din nou.")
        return PERSONAL_ADD_ITEM

    item_name, quantity = parse_item_input(text)
    if not item_name:
        await update.message.reply_text("❌ Nume invalid. Încearcă din nou.")
        return PERSONAL_ADD_ITEM

    await db_personal.add_item(user_id, item_name, quantity)
    log_action(user_id, "add personal item", item_name)

    items = await db_personal.get_items(user_id)
    text  = format_personal_list(items)
    kb    = personal_list_kb(items)

    await update.message.reply_text(
        f"✅ Adăugat: <b>{esc(item_name)}</b>\n\n" + text,
        parse_mode="HTML",
        reply_markup=kb,
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Toggle checked
# ---------------------------------------------------------------------------

async def toggle_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    item_id = int(query.data.split("_")[2])
    await db_personal.toggle_item(item_id, user_id)
    log_action(user_id, "toggle personal item", str(item_id))

    items = await db_personal.get_items(user_id)
    await query.edit_message_text(
        format_personal_list(items),
        parse_mode="HTML",
        reply_markup=personal_list_kb(items) if items else personal_empty_kb(),
    )


# ---------------------------------------------------------------------------
# Ștergere produs
# ---------------------------------------------------------------------------

async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    item_id = int(query.data.split("_")[2])
    item    = await db_personal.get_item(item_id, user_id)
    name    = item["item"] if item else "?"

    await db_personal.delete_item(item_id, user_id)
    log_action(user_id, "delete personal item", str(item_id))

    items = await db_personal.get_items(user_id)
    await query.answer(f"🗑 Șters: {name}", show_alert=False)
    await query.edit_message_text(
        format_personal_list(items),
        parse_mode="HTML",
        reply_markup=personal_list_kb(items) if items else personal_empty_kb(),
    )


# ---------------------------------------------------------------------------
# Șterge produse bifate
# ---------------------------------------------------------------------------

async def clear_checked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    count = await db_personal.clear_checked(user_id)
    log_action(user_id, "clear checked personal", str(count))

    items = await db_personal.get_items(user_id)
    await query.edit_message_text(
        format_personal_list(items),
        parse_mode="HTML",
        reply_markup=personal_list_kb(items) if items else personal_empty_kb(),
    )


# ---------------------------------------------------------------------------
# Partajare listă personală într-un grup
# ---------------------------------------------------------------------------

async def share_list_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Afișează grupurile în care userul e membru pentru a alege destinația."""
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    groups = await db_groups.get_user_groups(user_id)
    if not groups:
        await query.edit_message_text(
            "ℹ️ Nu faci parte din niciun grup.\n\n"
            "Creează sau alătură-te unui grup pentru a putea partaja.",
            parse_mode="HTML",
            reply_markup=__import__("keyboards.personal", fromlist=["personal_empty_kb"]).personal_empty_kb(),
        )
        return

    await query.edit_message_text(
        "📤 <b>Partajează în grup</b>\n\nAlege grupul în care să copiezi produsele necumpărate:",
        parse_mode="HTML",
        reply_markup=share_groups_kb(groups),
    )


async def share_list_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Copiază produsele necumpărate din lista personală în grupul ales."""
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[3])

    # Verificăm că userul e în grup
    if not await db_groups.is_member(group_id, user_id):
        await query.answer("❌ Nu ești membru al acestui grup.", show_alert=True)
        return

    items = await db_personal.get_items(user_id)
    pending = [i for i in items if not i["checked"]]

    if not pending:
        await query.answer("Lista personală nu are produse necumpărate.", show_alert=True)
        return

    count = await db_groups.copy_personal_to_group(user_id, group_id, pending)
    group = await db_groups.get_group(group_id)
    log_action(user_id, "share to group", f"{count} items -> group {group_id}")

    await query.edit_message_text(
        f'✅ <b>{count} produse</b> copiate în grupul "{esc(group["name"])}".',
        parse_mode="HTML",
        reply_markup=__import__("keyboards.main_menu", fromlist=["main_menu_kb"]).main_menu_kb(),
    )


# ---------------------------------------------------------------------------
# Fallback FSM — anulare
# ---------------------------------------------------------------------------

async def cancel_personal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    return await go_to_main_menu_end(query)
