"""
Handlers pentru grupuri: vizualizare, creare, alăturare, lista grupului.
Fluxuri FSM: GROUP_CREATE_NAME, GROUP_JOIN_CODE, GROUP_ADD_ITEM.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import database.groups as db_groups
from database.users import ensure_user
from keyboards.groups import (
    my_groups_kb,
    group_list_kb,
    group_empty_kb,
    group_cancel_kb,
    members_kb,
    join_cancel_kb,
    create_cancel_kb,
    confirm_leave_kb,
)
from keyboards.main_menu import main_menu_kb
from utils.helpers import (
    format_group_list,
    go_to_main_menu_end,
    parse_item_input,
    log_action,
    esc,
)
from utils.states import GROUP_CREATE_NAME, GROUP_JOIN_CODE, GROUP_ADD_ITEM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Grupurile mele
# ---------------------------------------------------------------------------

async def show_my_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    groups = await db_groups.get_user_groups(user_id)
    if not groups:
        await query.edit_message_text(
            "👥 <b>Grupurile mele</b>\n\nNu faci parte din niciun grup.\n"
            "Creează unul sau alătură-te cu un cod de invitație.",
            parse_mode="HTML",
            reply_markup=my_groups_kb([]),
        )
        return

    lines = ["👥 <b>Grupurile mele</b>\n"]
    for g in groups:
        cnt = await db_groups.member_count(g["id"])
        lines.append(f"  • {esc(g['name'])} — {cnt} membri")

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=my_groups_kb(groups),
    )
    log_action(user_id, "view my groups", str(len(groups)))


# ---------------------------------------------------------------------------
# Vizualizare lista unui grup
# ---------------------------------------------------------------------------

async def show_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[2])

    if not await db_groups.is_member(group_id, user_id):
        await query.answer("❌ Nu ești membru al acestui grup.", show_alert=True)
        return

    group = await db_groups.get_group(group_id)
    if not group:
        await query.answer("❌ Grupul nu mai există.", show_alert=True)
        return

    items   = await db_groups.get_group_items(group_id)
    cnt     = await db_groups.member_count(group_id)
    text    = format_group_list(items, group["name"], cnt)
    kb      = group_list_kb(items, group_id) if items else group_empty_kb(group_id)

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    log_action(user_id, "view group", str(group_id))


# ---------------------------------------------------------------------------
# Membri grup
# ---------------------------------------------------------------------------

async def show_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[2])

    group   = await db_groups.get_group(group_id)
    members = await db_groups.get_members(group_id)

    lines = [f'👥 <b>Membrii grupului "{esc(group["name"])}"</b>\n']
    for m in members:
        name = esc(m["first_name"] or m["username"] or f"User #{m['user_id']}")
        crown = " 👑" if m["user_id"] == group["owner_id"] else ""
        lines.append(f"  • {name}{crown}")

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=members_kb(members, group_id, group["owner_id"], user_id),
    )


# ---------------------------------------------------------------------------
# Adăugare produs în grup — FSM
# ---------------------------------------------------------------------------

async def start_add_group_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    await query.answer()
    group_id = int(query.data.split("_")[2])
    context.user_data["current_group_id"] = group_id

    await query.edit_message_text(
        "✏️ <b>Adaugă produs în grup</b>\n\n"
        "Scrie numele produsului (opțional cantitatea):\n"
        "<code>pâine</code>  sau  <code>pâine 3</code>",
        parse_mode="HTML",
        reply_markup=group_cancel_kb(group_id),
    )
    return GROUP_ADD_ITEM


async def receive_add_group_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id  = update.effective_user.id
    group_id = context.user_data.get("current_group_id")
    text     = update.message.text.strip()

    if not group_id:
        return ConversationHandler.END

    if not text:
        await update.message.reply_text("❌ Textul nu poate fi gol.")
        return GROUP_ADD_ITEM

    item_name, quantity = parse_item_input(text)
    await db_groups.add_group_item(group_id, item_name, quantity, user_id)
    log_action(user_id, "add group item", f"{item_name} -> group {group_id}")

    group  = await db_groups.get_group(group_id)
    items  = await db_groups.get_group_items(group_id)
    cnt    = await db_groups.member_count(group_id)

    await update.message.reply_text(
        f"✅ Adăugat: <b>{esc(item_name)}</b>\n\n" + format_group_list(items, group["name"], cnt),
        parse_mode="HTML",
        reply_markup=group_list_kb(items, group_id),
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Toggle / delete produse grup
# ---------------------------------------------------------------------------

async def toggle_group_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    parts    = query.data.split("_")   # g_chk_{item_id}_{group_id}
    item_id  = int(parts[2])
    group_id = int(parts[3])

    if not await db_groups.is_member(group_id, user_id):
        await query.answer("❌ Nu ești membru al acestui grup.", show_alert=True)
        return

    await db_groups.toggle_group_item(item_id, group_id)
    await _refresh_group(query, group_id)


async def delete_group_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    parts    = query.data.split("_")   # g_del_{item_id}_{group_id}
    item_id  = int(parts[2])
    group_id = int(parts[3])

    if not await db_groups.is_member(group_id, user_id):
        await query.answer("❌ Nu ești membru al acestui grup.", show_alert=True)
        return

    item = await db_groups.get_group_item(item_id, group_id)
    name = item["item"] if item else "?"
    await db_groups.delete_group_item(item_id, group_id)
    await query.answer(f"🗑 Șters: {name}")
    await _refresh_group(query, group_id)


async def clear_group_checked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[2])

    if not await db_groups.is_member(group_id, user_id):
        await query.answer("❌ Nu ești membru.", show_alert=True)
        return

    items = await db_groups.get_group_items(group_id)
    for item in items:
        if item["checked"]:
            await db_groups.delete_group_item(item["id"], group_id)

    await _refresh_group(query, group_id)


async def _refresh_group(query, group_id: int) -> None:
    group = await db_groups.get_group(group_id)
    items = await db_groups.get_group_items(group_id)
    cnt   = await db_groups.member_count(group_id)
    text  = format_group_list(items, group["name"], cnt)
    kb    = group_list_kb(items, group_id) if items else group_empty_kb(group_id)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)


# ---------------------------------------------------------------------------
# Cod invitație
# ---------------------------------------------------------------------------

async def show_invite_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[2])

    group = await db_groups.get_group(group_id)
    if not group or group["owner_id"] != user_id:
        await query.answer("❌ Doar ownerul poate vedea codul.", show_alert=True)
        return

    bot_user = await context.bot.get_me()
    deep_link = f"https://t.me/{bot_user.username}?start=join_{group['invite_code']}"

    from keyboards.groups import group_edit_kb
    await query.edit_message_text(
        f"🔗 <b>Cod de invitație</b>\n\n"
        f"Grup: <b>{esc(group['name'])}</b>\n\n"
        f"Cod: <code>{group['invite_code']}</code>\n\n"
        f"Link direct:\n{deep_link}",
        parse_mode="HTML",
        reply_markup=group_edit_kb(group_id),
    )


# ---------------------------------------------------------------------------
# Creare grup — FSM
# ---------------------------------------------------------------------------

async def start_create_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "➕ <b>Creează grup nou</b>\n\nScrie numele grupului:",
        parse_mode="HTML",
        reply_markup=create_cancel_kb(),
    )
    return GROUP_CREATE_NAME


async def receive_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id  = update.effective_user.id
    name     = update.message.text.strip()

    if not name:
        await update.message.reply_text("❌ Numele nu poate fi gol.")
        return GROUP_CREATE_NAME

    if len(name) > 50:
        await update.message.reply_text("❌ Numele e prea lung (max 50 caractere).")
        return GROUP_CREATE_NAME

    group_id = await db_groups.create_group(name, user_id)
    group    = await db_groups.get_group(group_id)
    log_action(user_id, "create group", f"{name} -> id={group_id}")

    bot_user  = await context.bot.get_me()
    deep_link = f"https://t.me/{bot_user.username}?start=join_{group['invite_code']}"

    from keyboards.groups import group_empty_kb
    await update.message.reply_text(
        f"✅ Grup creat: <b>{esc(name)}</b>\n\n"
        f"🔗 Cod invitație: <code>{group['invite_code']}</code>\n"
        f"Link: {deep_link}\n\n"
        "Trimite codul prietenilor ca să se alăture.",
        parse_mode="HTML",
        reply_markup=group_empty_kb(group_id),
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Alăturare grup prin cod — FSM
# ---------------------------------------------------------------------------

async def start_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # Dacă există cod din deep-link
    pending = context.user_data.pop("pending_join_code", None)
    if pending:
        context.user_data["join_code_prefill"] = pending

    await query.edit_message_text(
        "🔗 <b>Alătură-te unui grup</b>\n\nScrie codul de invitație (6 caractere):"
        + (f"\n\n<i>Cod detectat: <code>{pending}</code></i>" if pending else ""),
        parse_mode="HTML",
        reply_markup=join_cancel_kb(),
    )
    return GROUP_JOIN_CODE


async def receive_join_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    code    = update.message.text.strip().upper()

    group = await db_groups.get_group_by_code(code)
    if not group:
        await update.message.reply_text(
            "❌ Cod invalid. Verifică și încearcă din nou, sau anulează.",
            reply_markup=join_cancel_kb(),
        )
        return GROUP_JOIN_CODE

    already = await db_groups.is_member(group["id"], user_id)
    if already:
        from keyboards.groups import group_list_kb, group_empty_kb
        items = await db_groups.get_group_items(group["id"])
        cnt   = await db_groups.member_count(group["id"])
        await update.message.reply_text(
            f'ℹ️ Ești deja în grupul "{esc(group["name"])}".',
            parse_mode="HTML",
            reply_markup=group_list_kb(items, group["id"]) if items else group_empty_kb(group["id"]),
        )
        return ConversationHandler.END

    await db_groups.add_member(group["id"], user_id)
    log_action(user_id, "join group", f"group {group['id']}")

    items = await db_groups.get_group_items(group["id"])
    cnt   = await db_groups.member_count(group["id"])
    from keyboards.groups import group_list_kb, group_empty_kb
    await update.message.reply_text(
        f"✅ Te-ai alăturat grupului <b>{esc(group['name'])}</b>!\n"
        f"👥 Membri: {cnt}\n\n"
        + format_group_list(items, group["name"], cnt),
        parse_mode="HTML",
        reply_markup=group_list_kb(items, group["id"]) if items else group_empty_kb(group["id"]),
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Ieșire din grup
# ---------------------------------------------------------------------------

async def confirm_leave(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    group_id = int(query.data.split("_")[2])
    group    = await db_groups.get_group(group_id)

    await query.edit_message_text(
        f"⚠️ Ești sigur că vrei să ieși din grupul <b>{esc(group['name'])}</b>?",
        parse_mode="HTML",
        reply_markup=confirm_leave_kb(group_id),
    )


async def execute_leave(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    group_id = int(query.data.split("_")[3])
    group    = await db_groups.get_group(group_id)

    if group and group["owner_id"] == user_id:
        await query.edit_message_text(
            "❌ Ești ownerul grupului. Trebuie să îl ștergi sau să transferi ownership-ul.",
            parse_mode="HTML",
            reply_markup=main_menu_kb(),
        )
        return

    await db_groups.remove_member(group_id, user_id)
    log_action(user_id, "leave group", str(group_id))
    name = group["name"] if group else "grup șters"

    await query.edit_message_text(
        f"👋 Ai ieșit din grupul <b>{esc(name)}</b>.",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ---------------------------------------------------------------------------
# Fallback FSM
# ---------------------------------------------------------------------------

async def cancel_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    return await go_to_main_menu_end(query)
