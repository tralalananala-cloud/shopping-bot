"""
Toți handlerii de comenzi și mesaje pentru botul de cumpărături.
"""

import html
import logging

from telegram import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

import storage
from config import CATEGORIES, DEFAULT_CATEGORY

logger = logging.getLogger(__name__)

# Textele butoanelor din tastatura persistentă
BTN_LIST    = "📋 Lista mea"
BTN_ADD     = "➕ Adaugă produs"
BTN_UNDO    = "↩️ Undo"
BTN_SHARE   = "📤 Partajează"
BTN_INVITE  = "👥 Invită"
BTN_MEMBERS = "👤 Membri"
BTN_HELP    = "❓ Ajutor"

# ---------------------------------------------------------------------------
# Texte statice
# ---------------------------------------------------------------------------

WELCOME_TEXT = (
    "👋 Bun venit la <b>BotListă</b>!\n\n"
    "Scrie direct un produs ca să-l adaugi, sau folosește butoanele de jos.\n\n"
    "<b>Partajare cu familia/prietenii:</b>\n"
    "• /invite — generează un cod de invitație\n"
    "• /join &lt;cod&gt; — alătură-te listei altcuiva\n\n"
    "Scrie /help pentru toate comenzile disponibile."
)

HELP_TEXT = (
    "📖 <b>Ajutor detaliat</b>\n\n"
    "<b>Adăugare produse:</b>\n"
    "• Scrie orice text — se adaugă automat\n"
    "• <code>lapte, pâine, ouă</code> — mai multe odată\n"
    "• <code>/add lapte #lactate</code> — cu categorie\n\n"
    "<b>Categorii:</b>\n"
    "🥛 <code>#lactate</code>  🥩 <code>#carne</code>  🥦 <code>#legume</code>\n"
    "🍎 <code>#fructe</code>  🧴 <code>#igiena</code>  🍞 <code>#panificatie</code>\n"
    "🛒 <code>#altele</code> (implicit)\n\n"
    "<b>Gestionare:</b>\n"
    "• Apasă pe produs în listă ca să-l bifezi\n"
    "• Apasă 🗑 ca să-l ștergi\n"
    "• <code>/done 3</code> — bifează/debifează nr. 3\n"
    "• <code>/remove 3</code> — șterge nr. 3\n"
    "• <code>/clear</code> — golește tot\n"
    "• <code>/undo</code> — anulează ultima acțiune\n\n"
    "<b>Lista partajată:</b>\n"
    "• /invite — generează cod de invitație\n"
    "• /join &lt;cod&gt; — alătură-te unui grup\n"
    "• /members — vezi membrii grupului\n"
    "• /leave — ieși din grupul partajat\n\n"
    "<b>Vizualizare &amp; partajare:</b>\n"
    "• /list sau 📋 — afișează lista\n"
    "• /share sau 📤 — text simplu de copiat"
)

# ---------------------------------------------------------------------------
# Tastatura persistentă
# ---------------------------------------------------------------------------

def _main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [BTN_LIST,   BTN_ADD],
            [BTN_UNDO,   BTN_SHARE],
            [BTN_INVITE, BTN_MEMBERS, BTN_HELP],
        ],
        resize_keyboard=True,
        input_field_placeholder="Scrie un produs sau alege o acțiune...",
    )


async def _r(update: Update, text: str, parse_mode: str = None) -> None:
    """
    Helper: trimite răspuns cu tastatura persistentă ÎNTOTDEAUNA atașată.
    Folosit pentru orice mesaj care nu are InlineKeyboardMarkup propriu.
    """
    await update.message.reply_text(
        text, parse_mode=parse_mode, reply_markup=_main_keyboard()
    )

# ---------------------------------------------------------------------------
# Formatare mesaje
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    return html.escape(text)


def _progress_bar(done: int, total: int, length: int = 8) -> str:
    if total == 0:
        return ""
    filled = round(done / total * length)
    return "🟩" * filled + "⬜" * (length - filled)


def _format_list(items: list) -> str:
    if not items:
        return (
            "📭 <b>Lista este goală.</b>\n\n"
            "Apasă <b>➕ Adaugă produs</b> sau scrie direct un produs."
        )

    done_count = sum(1 for i in items if i["done"])
    total = len(items)
    bar = _progress_bar(done_count, total)

    by_category = {}
    for idx, item in enumerate(items, 1):
        cat = item.get("category", DEFAULT_CATEGORY)
        by_category.setdefault(cat, []).append((idx, item))

    lines = [
        "🛒 <b>Lista de cumpărături</b>",
        f"{bar}  <b>{done_count}/{total}</b> cumpărate\n",
    ]

    for cat_key, cat_items in by_category.items():
        cat_label = CATEGORIES.get(cat_key, "🛒 Altele")
        lines.append(f"<b>{cat_label}</b>")
        for idx, item in cat_items:
            safe = _esc(item["name"])
            if item["done"]:
                lines.append(f"  ✅ <s>{safe}</s>")
            else:
                lines.append(f"  ⬜ {safe}")
        lines.append("")

    return "\n".join(lines).rstrip()


def _format_list_compact(items: list) -> str:
    """
    Versiune compactă pentru notificări: doar bara de progres
    și produsele NECUMPĂRATE (maximum 10).
    """
    if not items:
        return "📭 Lista este acum goală."

    done_count = sum(1 for i in items if i["done"])
    total = len(items)
    bar = _progress_bar(done_count, total)
    pending = [i for i in items if not i["done"]]

    lines = [f"{bar}  <b>{done_count}/{total}</b> cumpărate"]
    if pending:
        lines.append("\n<b>De cumpărat:</b>")
        for item in pending[:10]:
            lines.append(f"  ⬜ {_esc(item['name'])}")
        if len(pending) > 10:
            lines.append(f"  <i>… și alte {len(pending) - 10} produse</i>")

    return "\n".join(lines)


def _list_with_item_buttons(items: list) -> InlineKeyboardMarkup:
    rows = []
    for idx, item in enumerate(items, 1):
        icon = "✅" if item["done"] else "⬜"
        name = item["name"]
        label = f"{icon} {name}" if len(name) <= 24 else f"{icon} {name[:22]}…"
        rows.append([
            InlineKeyboardButton(label, callback_data=f"t_{idx}"),
            InlineKeyboardButton("🗑",   callback_data=f"d_{idx}"),
        ])
    rows.append([
        InlineKeyboardButton("✅ Toate",   callback_data="mark_all"),
        InlineKeyboardButton("🧹 Golește", callback_data="clear_confirm"),
    ])
    return InlineKeyboardMarkup(rows)


def _confirm_clear_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Da, golește", callback_data="clear_yes"),
        InlineKeyboardButton("❌ Anulează",    callback_data="clear_no"),
    ]])


def _index_error_msg(index: int, items: list) -> str:
    if not items:
        return "❌ Lista este goală."
    return (
        f"❌ Nu există produsul nr. <b>{index}</b>. "
        f"Lista are <b>{len(items)}</b> produse."
    )

# ---------------------------------------------------------------------------
# Notificări pentru membrii grupului
# ---------------------------------------------------------------------------

async def _notify_others(
    context: ContextTypes.DEFAULT_TYPE,
    sender_id: int,
    sender_name: str,
    action_text: str,
) -> None:
    """
    Trimite o notificare compactă (acțiune + stare listă)
    tuturor celorlalți membri din grup.
    """
    members = storage.get_group_members(sender_id)
    if len(members) <= 1:
        return  # nu e grup partajat

    items = storage.get_items(sender_id)
    summary = _format_list_compact(items)
    message = f"🔔 <b>{_esc(sender_name)}</b> {action_text}\n\n{summary}"

    for member_id in members:
        if member_id == sender_id:
            continue
        try:
            await context.bot.send_message(
                chat_id=member_id,
                text=message,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("Nu am putut notifica userul %s: %s", member_id, e)


def _sender_name(update: Update) -> str:
    user = update.effective_user
    return user.first_name or user.username or "Cineva"

# ---------------------------------------------------------------------------
# Helper reutilizabil — confirmare adăugare
# ---------------------------------------------------------------------------

async def _reply_added(update: Update, added: list) -> None:
    if len(added) == 1:
        await _r(update, f"✅ Adăugat: <b>{_esc(added[0])}</b>", parse_mode="HTML")
    else:
        names = "\n".join(f"  • {_esc(n)}" for n in added)
        await _r(update, f"✅ Adăugate <b>{len(added)}</b> produse:\n{names}", parse_mode="HTML")


async def _refresh_list_message(query, user_id: int) -> None:
    items = storage.get_items(user_id)
    text = _format_list(items)
    if items:
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=_list_with_item_buttons(items),
        )
    else:
        await query.edit_message_text(text, parse_mode="HTML")

# ---------------------------------------------------------------------------
# Funcții helper — parsare produse
# ---------------------------------------------------------------------------

def _parse_category(text: str):
    parts = text.strip().split("#", 1)
    name = parts[0].strip()
    if len(parts) == 2:
        raw = (parts[1].strip().lower()
               .replace("ă", "a").replace("â", "a")
               .replace("î", "i")
               .replace("ș", "s").replace("ț", "t"))
        if raw in CATEGORIES:
            return name, raw
    return name, DEFAULT_CATEGORY


def _split_products(text: str):
    return [r.strip() for r in text.replace("\n", ",").split(",") if r.strip()]


def _add_products(user_id: int, text: str):
    added = []
    for raw in _split_products(text):
        name, cat = _parse_category(raw)
        if name:
            storage.add_item(user_id, name, cat)
            added.append(name)
    return added

# ---------------------------------------------------------------------------
# Handleri de comenzi — liste
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT, parse_mode="HTML",
        reply_markup=_main_keyboard(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _r(update, HELP_TEXT, parse_mode="HTML")


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = " ".join(context.args).strip() if context.args else ""
    if not text:
        await _r(update,
            "❌ Folosire: /add &lt;produs&gt;\n"
            "Exemplu: <code>/add lapte #lactate</code>",
            parse_mode="HTML")
        return
    added = _add_products(user_id, text)
    if not added:
        await _r(update, "❌ Nu am putut identifica niciun produs valid.")
        return
    await _reply_added(update, added)
    names = ", ".join(added)
    await _notify_others(context, user_id, _sender_name(update),
                         f"a adăugat: <b>{_esc(names)}</b>")


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    items = storage.get_items(user_id)

    # Indicăm dacă lista e partajată
    members = storage.get_group_members(user_id)
    header = ""
    if len(members) > 1:
        header = f"👥 <i>Listă partajată cu {len(members)} membri</i>\n\n"

    text = header + _format_list(items)
    if items:
        await update.message.reply_text(
            text, parse_mode="HTML",
            reply_markup=_list_with_item_buttons(items),
        )
    else:
        await _r(update, text, parse_mode="HTML")


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await _r(update,
            "❌ Folosire: /done &lt;număr&gt;\nExemplu: <code>/done 3</code>",
            parse_mode="HTML")
        return
    try:
        index = int(context.args[0])
    except ValueError:
        await _r(update, "❌ Numărul trebuie să fie un întreg.")
        return
    item = storage.toggle_done(user_id, index)
    if item is None:
        items = storage.get_items(user_id)
        await _r(update, _index_error_msg(index, items), parse_mode="HTML")
        return
    status = "✅ Cumpărat" if item["done"] else "⬜ Necumpărat"
    await _r(update, f"{status}: <b>{_esc(item['name'])}</b>", parse_mode="HTML")
    verb = "a bifat" if item["done"] else "a debifat"
    await _notify_others(context, user_id, _sender_name(update),
                         f"{verb}: <b>{_esc(item['name'])}</b>")


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await _r(update,
            "❌ Folosire: /remove &lt;număr&gt;\nExemplu: <code>/remove 3</code>",
            parse_mode="HTML")
        return
    try:
        index = int(context.args[0])
    except ValueError:
        await _r(update, "❌ Numărul trebuie să fie un întreg.")
        return
    item = storage.remove_item(user_id, index)
    if item is None:
        items = storage.get_items(user_id)
        await _r(update, _index_error_msg(index, items), parse_mode="HTML")
        return
    await _r(update, f"🗑 Șters: <b>{_esc(item['name'])}</b>", parse_mode="HTML")
    await _notify_others(context, user_id, _sender_name(update),
                         f"a șters: <b>{_esc(item['name'])}</b>")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    items = storage.get_items(user_id)
    if not items:
        await _r(update, "📭 Lista este deja goală.")
        return
    await update.message.reply_text(
        f"⚠️ Ești sigur că vrei să ștergi <b>{len(items)} produse</b>?",
        parse_mode="HTML",
        reply_markup=_confirm_clear_keyboard(),
    )


async def cmd_undo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    result = storage.undo(user_id)
    if result is None:
        await _r(update, "↩️ Nu există acțiuni de anulat.")
    else:
        await _r(update, f"↩️ {_esc(result)}", parse_mode="HTML")
        await _notify_others(context, user_id, _sender_name(update),
                             f"a anulat o acțiune: <i>{_esc(result)}</i>")


async def cmd_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    items = storage.get_items(user_id)
    if not items:
        await _r(update, "📭 Lista este goală. Nu ai ce partaja.")
        return
    pending = [i for i in items if not i["done"]]
    done    = [i for i in items if i["done"]]
    lines   = ["🛒 Lista de cumpărături:\n"]
    if pending:
        lines.append("De cumpărat:")
        for item in pending:
            lines.append(f"  ☐ {item['name']}")
    if done:
        lines.append("\nCumpărate deja:")
        for item in done:
            lines.append(f"  ✓ {item['name']}")
    lines.append(f"\n({len(done)}/{len(items)} cumpărate)")
    await _r(update, "\n".join(lines))

# ---------------------------------------------------------------------------
# Handleri de comenzi — grup partajat
# ---------------------------------------------------------------------------

async def cmd_invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generează și afișează codul de invitație al grupului."""
    user_id = update.effective_user.id
    code = storage.generate_invite_code(user_id)
    bot_username = (await context.bot.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start=join_{code}"

    await _r(update,
        f"🔗 <b>Invită pe cineva în lista ta</b>\n\n"
        f"Codul de invitație:\n"
        f"<code>{code}</code>\n\n"
        f"Sau trimite-le link-ul direct:\n"
        f"{deep_link}\n\n"
        f"<i>Ei trebuie să trimită /join {code} botului.</i>",
        parse_mode="HTML")


async def cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Alătură userul la un grup prin cod."""
    user_id = update.effective_user.id

    # Suport deep link: /start join_ABCDEF
    code = ""
    if context.args:
        arg = context.args[0]
        code = arg.replace("join_", "").strip().upper()

    if not code:
        await _r(update,
            "❌ Folosire: /join &lt;cod&gt;\n"
            "Exemplu: <code>/join ABC123</code>",
            parse_mode="HTML")
        return

    success, result = storage.join_group_by_code(user_id, code)
    if not success:
        await _r(update, f"❌ {_esc(result)}")
        return

    owner_id = result
    items = storage.get_items(user_id)
    members = storage.get_group_members(user_id)

    await _r(update,
        f"✅ Te-ai alăturat grupului partajat!\n"
        f"👥 Membri: <b>{len(members)}</b> | "
        f"Produse în listă: <b>{len(items)}</b>\n\n"
        f"Folosește 📋 Lista mea ca să vezi lista.",
        parse_mode="HTML")

    # Notificăm ceilalți membri
    name = _sender_name(update)
    for member_id in members:
        if member_id == user_id:
            continue
        try:
            await context.bot.send_message(
                chat_id=member_id,
                text=f"👋 <b>{_esc(name)}</b> s-a alăturat listei partajate!",
                parse_mode="HTML",
            )
        except Exception:
            pass


async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Iese din grupul partajat."""
    user_id = update.effective_user.id
    name = _sender_name(update)

    # Notificăm înainte de a ieși
    members = storage.get_group_members(user_id)

    success = storage.leave_group(user_id)
    if not success:
        await _r(update, "ℹ️ Nu ești într-un grup partajat. Folosești deja lista personală.")
        return

    await _r(update, "👋 Ai ieșit din lista partajată.\nAcum folosești lista ta personală.")

    for member_id in members:
        if member_id == user_id:
            continue
        try:
            await context.bot.send_message(
                chat_id=member_id,
                text=f"👋 <b>{_esc(name)}</b> a ieșit din lista partajată.",
                parse_mode="HTML",
            )
        except Exception:
            pass


async def cmd_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Afișează membrii grupului curent."""
    user_id = update.effective_user.id
    members = storage.get_group_members(user_id)
    owner_id = storage.get_group_owner(user_id)

    if len(members) <= 1:
        code = storage.generate_invite_code(user_id)
        await _r(update,
            f"👤 Ești singur în lista ta.\n\n"
            f"Invită pe cineva cu codul: <code>{code}</code>\n"
            f"sau cu comanda /invite",
            parse_mode="HTML")
        return

    lines = [f"👥 <b>Membrii grupului ({len(members)}):</b>\n"]
    for mid in members:
        role = " 👑" if mid == owner_id else ""
        lines.append(f"  • user <code>{mid}</code>{role}")
    lines.append("\n<i>👑 = proprietar grup</i>")

    await _r(update, "\n".join(lines), parse_mode="HTML")

# ---------------------------------------------------------------------------
# Handler text liber + butoane tastatură persistentă
# ---------------------------------------------------------------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    if not text:
        return

    # Butoane tastatură persistentă
    if text == BTN_LIST:
        await cmd_list(update, context)
        return
    if text == BTN_UNDO:
        await cmd_undo(update, context)
        return
    if text == BTN_SHARE:
        await cmd_share(update, context)
        return
    if text == BTN_ADD:
        await update.message.reply_text(
            "✏️ Scrie produsul (sau mai multe separate prin virgulă):",
            reply_markup=ForceReply(
                input_field_placeholder="ex: lapte, pâine #panificatie"
            ),
        )
        return
    if text == BTN_INVITE:
        await cmd_invite(update, context)
        return
    if text == BTN_MEMBERS:
        await cmd_members(update, context)
        return
    if text == BTN_HELP:
        await cmd_help(update, context)
        return

    # Deep link via /start join_CODE
    if text.startswith("/start join_"):
        context.args = [text.split("join_", 1)[1]]
        await cmd_join(update, context)
        return

    # Orice alt text → adaugă ca produs
    user_id = update.effective_user.id
    added = _add_products(user_id, text)
    if not added:
        await _r(update, "❓ Nu am înțeles. Scrie un produs sau apasă /help.")
        return

    await _reply_added(update, added)
    names = ", ".join(added)
    await _notify_others(context, user_id, _sender_name(update),
                         f"a adăugat: <b>{_esc(names)}</b>")

# ---------------------------------------------------------------------------
# Handler butoane inline
# ---------------------------------------------------------------------------

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    name = update.effective_user.first_name or "Cineva"
    data = query.data

    if data.startswith("t_"):
        idx = int(data[2:])
        item = storage.toggle_done(user_id, idx)
        if item is None:
            await query.answer("Produsul nu mai există în listă.", show_alert=True)
            return
        await _refresh_list_message(query, user_id)
        verb = "a bifat" if item["done"] else "a debifat"
        await _notify_others(context, user_id, name,
                             f"{verb}: <b>{_esc(item['name'])}</b>")
        return

    if data.startswith("d_"):
        idx = int(data[2:])
        item = storage.remove_item(user_id, idx)
        if item is None:
            await query.answer("Produsul nu mai există în listă.", show_alert=True)
            return
        await query.answer(f"🗑 Șters: {item['name']}")
        await _refresh_list_message(query, user_id)
        await _notify_others(context, user_id, name,
                             f"a șters: <b>{_esc(item['name'])}</b>")
        return

    if data == "mark_all":
        count = storage.mark_all_done(user_id)
        if count == 0:
            await query.answer("Toate produsele sunt deja bifate! ✅", show_alert=True)
        else:
            await query.answer(f"✅ {count} produse marcate.")
            await _refresh_list_message(query, user_id)
            await _notify_others(context, user_id, name,
                                 f"a marcat toate <b>{count} produse</b> ca cumpărate")
        return

    if data == "clear_confirm":
        items = storage.get_items(user_id)
        if not items:
            await query.edit_message_text("📭 Lista este deja goală.")
            return
        await query.edit_message_text(
            f"⚠️ Ești sigur că vrei să ștergi <b>{len(items)} produse</b>?",
            parse_mode="HTML",
            reply_markup=_confirm_clear_keyboard(),
        )
        return

    if data == "clear_yes":
        count = storage.clear_items(user_id)
        await query.edit_message_text(
            f"🧹 Lista a fost golită.\n<i>{count} produse șterse.</i>",
            parse_mode="HTML",
        )
        await _notify_others(context, user_id, name,
                             f"a golit lista (<b>{count} produse</b> șterse)")
        return

    if data == "clear_no":
        await _refresh_list_message(query, user_id)
        return
