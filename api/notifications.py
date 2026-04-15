"""Trimitere notificări Telegram către membrii grupurilor."""

import html
import logging

import httpx

from config import BOT_TOKEN

logger = logging.getLogger(__name__)


async def _send(user_id: int, text: str) -> None:
    """Trimite un mesaj Telegram unui utilizator. Erorile sunt ignorate silențios."""
    if not BOT_TOKEN:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": user_id, "text": text, "parse_mode": "HTML"},
            )
    except Exception as e:
        logger.warning("Notificare eșuată pentru user_id=%s: %s", user_id, e)


async def notify_item_added(
    actor_name: str,
    item_name: str,
    group_name: str,
    member_ids: list[int],
    actor_id: int,
) -> None:
    """Notifică toți membrii (mai puțin actorul) că a fost adăugat un produs."""
    text = (
        f"🛒 <b>{html.escape(actor_name)}</b> a adăugat "
        f"<b>{html.escape(item_name)}</b> "
        f"în grupul <i>{html.escape(group_name)}</i>"
    )
    for uid in member_ids:
        if uid != actor_id:
            await _send(uid, text)


async def notify_item_checked(
    actor_name: str,
    item_name: str,
    group_name: str,
    member_ids: list[int],
    actor_id: int,
) -> None:
    """Notifică toți membrii că un produs a fost bifat ca îndeplinit."""
    text = (
        f"✅ <b>{html.escape(actor_name)}</b> a bifat "
        f"<b>{html.escape(item_name)}</b> "
        f"în grupul <i>{html.escape(group_name)}</i>"
    )
    for uid in member_ids:
        if uid != actor_id:
            await _send(uid, text)
