"""
Handlers pentru administrarea grupurilor (doar owner).
FSM: GROUP_RENAME.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import database.groups as db_groups
from keyboards.groups import (
    edit_groups_kb,
    group_edit_kb,
    confirm_delete_group_kb,
    rename_cancel_kb,
    members_kb,
)
from keyboards.main_menu import main_menu_kb
from utils.helpers import go_to_main_menu_end, log_action, esc
from utils.states import GROUP_RENAME

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Editare grupuri — lista grupurilor deținute
# ---------------------------------------------------------------------------

async def show_edit_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    all_groups = await db_groups.get_user_groups(user_id)
    owned      = [g for g in all_groups if g["owner_id"] == user_id]

    await query.edit_message_text(
        "⚙️ <b>Editează grupuri</b>\n\nAlege grupul pe care îl deții:",
        parse_mode="HTML",
        reply_markup=edit_groups_kb(owned),
    )


# ---------------------------------------------------------------------------
# Panou de control grup
# ---------------------------------------------------------------------------

async def show_group_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[2])

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        await query.answer("❌ Nu ai permisiunea să editezi acest grup.", show_alert=True)
        return

    cnt = await db_groups.member_count(group_id)
    await query.edit_message_text(
        f"⚙️ <b>Administrare grup</b>\n\n"
        f"Grup: <b>{esc(group['name'])}</b>\n"
        f"Membri: {cnt}\n"
        f"Cod invitație: <code>{group['invite_code']}</code>",
        parse_mode="HTML",
        reply_markup=group_edit_kb(group_id),
    )


# ---------------------------------------------------------------------------
# Redenumire grup — FSM
# ---------------------------------------------------------------------------

async def start_rename_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[2])

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        await query.answer("❌ Nu ai permisiunea.", show_alert=True)
        return ConversationHandler.END

    context.user_data["renaming_group_id"] = group_id

    await query.edit_message_text(
        f"✏️ <b>Redenumire grup</b>\n\n"
        f"Numele curent: <b>{esc(group['name'])}</b>\n\n"
        "Scrie noul nume:",
        parse_mode="HTML",
        reply_markup=rename_cancel_kb(group_id),
    )
    return GROUP_RENAME


async def receive_rename_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id  = update.effective_user.id
    group_id = context.user_data.get("renaming_group_id")
    new_name = update.message.text.strip()

    if not group_id:
        return ConversationHandler.END

    if not new_name:
        await update.message.reply_text("❌ Numele nu poate fi gol.")
        return GROUP_RENAME

    if len(new_name) > 50:
        await update.message.reply_text("❌ Numele e prea lung (max 50 caractere).")
        return GROUP_RENAME

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        return ConversationHandler.END

    await db_groups.rename_group(group_id, new_name)
    log_action(user_id, "rename group", f"{group_id} -> {new_name}")

    cnt = await db_groups.member_count(group_id)
    await update.message.reply_text(
        f"✅ Grup redenumit în <b>{esc(new_name)}</b>.",
        parse_mode="HTML",
        reply_markup=group_edit_kb(group_id),
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Eliminare membru
# ---------------------------------------------------------------------------

async def kick_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    parts    = query.data.split("_")   # g_kick_{group_id}_{target_uid}
    group_id = int(parts[2])
    target   = int(parts[3])

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        await query.answer("❌ Nu ai permisiunea.", show_alert=True)
        return

    if target == user_id:
        await query.answer("❌ Nu te poți elimina pe tine însuți.", show_alert=True)
        return

    await db_groups.remove_member(group_id, target)
    log_action(user_id, "kick member", f"{target} from group {group_id}")

    members = await db_groups.get_members(group_id)
    await query.edit_message_text(
        f"✅ Membrul a fost eliminat din grupul <b>{esc(group['name'])}</b>.",
        parse_mode="HTML",
        reply_markup=members_kb(members, group_id, group["owner_id"], user_id),
    )


# ---------------------------------------------------------------------------
# Ștergere grup
# ---------------------------------------------------------------------------

async def confirm_delete_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[3])

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        await query.answer("❌ Nu ai permisiunea.", show_alert=True)
        return

    await query.edit_message_text(
        f"⚠️ Ești sigur că vrei să ștergi grupul <b>{esc(group['name'])}</b>?\n"
        "Această acțiune este <b>ireversibilă</b> și șterge și lista grupului.",
        parse_mode="HTML",
        reply_markup=confirm_delete_group_kb(group_id),
    )


async def execute_delete_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[4])

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        await query.answer("❌ Nu ai permisiunea.", show_alert=True)
        return

    name = group["name"]
    await db_groups.delete_group(group_id)
    log_action(user_id, "delete group", str(group_id))

    await query.edit_message_text(
        f"🗑 Grupul <b>{esc(name)}</b> a fost șters.",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ---------------------------------------------------------------------------
# Fallback FSM
# ---------------------------------------------------------------------------

async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    return await go_to_main_menu_end(query)
