"""
Funcții helper reutilizabile: navigare, formatare, logging acțiuni.
"""

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards.main_menu import main_menu_kb

logger = logging.getLogger(__name__)

MAIN_MENU_TEXT = (
    "🏠 <b>Meniu principal</b>\n\n"
    "Bun venit! Alege o opțiune din meniu:"
)


def esc(text: str) -> str:
    """Escapează HTML pentru a preveni injecții în mesaje."""
    return html.escape(str(text))


# ---------------------------------------------------------------------------
# Navigare — meniu principal
# ---------------------------------------------------------------------------

async def go_to_main_menu(query) -> None:
    """
    Editează mesajul curent pentru a afișa meniul principal.
    Apelat din orice ecran prin butonul '🏠 Meniu principal'.
    """
    await query.edit_message_text(
        MAIN_MENU_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


async def go_to_main_menu_end(query) -> int:
    """
    Ca go_to_main_menu, dar returnează ConversationHandler.END
    pentru a ieși dintr-o conversație FSM.
    """
    await go_to_main_menu(query)
    return ConversationHandler.END


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Trimite meniul principal ca mesaj nou (folosit la /start)."""
    await update.message.reply_text(
        MAIN_MENU_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ---------------------------------------------------------------------------
# Formatare liste
# ---------------------------------------------------------------------------

def format_personal_list(items: list, user_name: str = None) -> str:
    if not items:
        return "📭 <b>Lista ta personală este goală.</b>\n\nApasă ➕ pentru a adăuga primul produs."

    done  = sum(1 for i in items if i["checked"])
    total = len(items)
    bar   = _progress_bar(done, total)

    header = f"📝 <b>Lista mea personală</b>"
    if user_name:
        header = f"📝 <b>Lista lui {esc(user_name)}</b>"

    lines = [header, f"{bar}  <b>{done}/{total}</b> cumpărate\n"]
    for item in items:
        qty  = f" ×{esc(item['quantity'])}" if item["quantity"] != "1" else ""
        name = esc(item["item"])
        if item["checked"]:
            lines.append(f"  ✅ <s>{name}</s>{qty}")
        else:
            lines.append(f"  ⬜ {name}{qty}")
    return "\n".join(lines)


def format_group_list(items: list, group_name: str, member_count: int) -> str:
    if not items:
        return (
            f'📭 <b>Lista grupului "{esc(group_name)}"</b> este goală.\n\n'
            "Apasă ➕ pentru a adăuga primul produs."
        )

    done  = sum(1 for i in items if i["checked"])
    total = len(items)
    bar   = _progress_bar(done, total)

    lines = [
        f"👥 <b>{esc(group_name)}</b>  •  {member_count} membri",
        f"{bar}  <b>{done}/{total}</b> cumpărate\n",
    ]
    for item in items:
        qty    = f" ×{esc(item['quantity'])}" if item["quantity"] != "1" else ""
        name   = esc(item["item"])
        adder  = esc(item["first_name"] or item["username"] or "?")
        if item["checked"]:
            lines.append(f"  ✅ <s>{name}</s>{qty} <i>({adder})</i>")
        else:
            lines.append(f"  ⬜ {name}{qty} <i>({adder})</i>")
    return "\n".join(lines)


def _progress_bar(done: int, total: int, length: int = 8) -> str:
    if total == 0:
        return ""
    filled = round(done / total * length)
    return "🟩" * filled + "⬜" * (length - filled)


# ---------------------------------------------------------------------------
# Parsare input produs ("lapte 2" → item="lapte", qty="2")
# ---------------------------------------------------------------------------

def parse_item_input(text: str):
    """Returnează (item_name, quantity)."""
    text = text.strip()
    parts = text.rsplit(None, 1)
    if len(parts) == 2 and parts[1].isdigit() and int(parts[1]) > 0:
        return parts[0].strip(), parts[1]
    return text, "1"


# ---------------------------------------------------------------------------
# Logging acțiuni
# ---------------------------------------------------------------------------

def log_action(user_id: int, action: str, detail: str = "") -> None:
    logger.info("[User %s] %s %s", user_id, action, detail)
