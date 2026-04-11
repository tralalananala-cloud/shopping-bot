"""
Autentificare prin Telegram WebApp initData.

Frontentul trimite header-ul:
    X-Telegram-Init-Data: <valoarea din window.Telegram.WebApp.initData>

Serverul validează semnătura HMAC-SHA256 cu BOT_TOKEN,
extrage user_id-ul și îl returnează ca dependency FastAPI.

Documentație Telegram:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import logging
from typing import Optional
from urllib.parse import parse_qsl, unquote

from fastapi import Header, HTTPException, status

import database.users as db_users
from config import BOT_TOKEN

logger = logging.getLogger(__name__)


def _validate_init_data(init_data: str) -> dict:
    """
    Validează initData-ul primit de la Telegram WebApp.
    Returnează dict-ul cu datele userului sau aruncă HTTPException 401.
    """
    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="initData invalid")

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Hash lipsă din initData")

    # Construim data_check_string: chei sortate alfabetic, separate prin \n
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    # Cheia secretă: HMAC-SHA256("WebAppData", BOT_TOKEN)
    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Semnătură initData invalidă")

    # Extragem datele userului
    raw_user = parsed.get("user", "{}")
    try:
        user_data = json.loads(unquote(raw_user))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Câmpul user din initData e invalid")

    return user_data


async def get_current_user(
    x_telegram_init_data: Optional[str] = Header(default=None),
    x_dev_user_id: Optional[str] = Header(default=None),
) -> int:
    """
    Dependency FastAPI — returnează user_id-ul autentificat.

    În producție: validează X-Telegram-Init-Data.
    În development: acceptă X-Dev-User-Id (număr întreg) — DEZACTIVEAZĂ în producție!
    """
    # --- Mod development (doar când nu există initData) ---
    if not x_telegram_init_data and x_dev_user_id:
        try:
            user_id = int(x_dev_user_id)
        except ValueError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="X-Dev-User-Id trebuie să fie un număr întreg")
        await db_users.ensure_user(user_id)
        logger.warning("DEV AUTH: user_id=%s (fără validare Telegram)", user_id)
        return user_id

    # --- Producție: validare Telegram initData ---
    if not x_telegram_init_data:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Header X-Telegram-Init-Data lipsă",
        )

    user_data = _validate_init_data(x_telegram_init_data)
    user_id = user_data.get("id")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="user_id lipsă din initData")

    await db_users.ensure_user(
        user_id=int(user_id),
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
    )
    return int(user_id)
