"""
Logica de salvare și citire a datelor.

Structura fișierului JSON:
{
  "users": {
    "user_id": "group_id"          # la ce grup aparține userul
  },
  "groups": {
    "group_id": {
      "items":       [...],
      "next_uid":    N,
      "history":     [...],
      "owner":       user_id_int,
      "invite_code": "ABC123" | null,
      "members":     [user_id1, user_id2, ...]
    }
  }
}

Un user fără grup partajat are group_id == str(user_id) — grup personal.
"""

import json
import logging
import os
import random
import string

from config import DATA_FILE, DEFAULT_CATEGORY, MAX_HISTORY

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# I/O de bază
# ---------------------------------------------------------------------------

def _load_all() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "groups": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Migrare format vechi {user_id: {items, ...}} -> format nou
        if "users" not in data and "groups" not in data:
            data = _migrate(data)
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Eroare la citire date: %s", e)
        return {"users": {}, "groups": {}}


def _save_all(data: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("Eroare la salvare date: %s", e)


def _migrate(old: dict) -> dict:
    """Migrează formatul vechi la cel nou."""
    new = {"users": {}, "groups": {}}
    for uid, udata in old.items():
        if isinstance(udata, dict) and "items" in udata:
            new["users"][uid] = uid
            new["groups"][uid] = {
                "items":       udata.get("items", []),
                "next_uid":    udata.get("next_uid", 1),
                "history":     udata.get("history", []),
                "owner":       int(uid),
                "invite_code": None,
                "members":     [int(uid)],
            }
    return new


# ---------------------------------------------------------------------------
# Gestionare utilizatori și grupuri
# ---------------------------------------------------------------------------

def _ensure_personal_group(data: dict, user_id: int) -> str:
    """Creează grupul personal al userului dacă nu există. Returnează group_id."""
    uid = str(user_id)
    gid = uid  # grupul personal are același id ca userul
    if gid not in data["groups"]:
        data["groups"][gid] = {
            "items":       [],
            "next_uid":    1,
            "history":     [],
            "owner":       user_id,
            "invite_code": None,
            "members":     [user_id],
        }
    return gid


def get_user_group_id(user_id: int) -> str:
    """Returnează group_id-ul curent al userului (personal sau partajat)."""
    data = _load_all()
    uid = str(user_id)
    if uid in data.get("users", {}):
        return data["users"][uid]
    # Prima interacțiune — creăm grupul personal
    gid = _ensure_personal_group(data, user_id)
    data["users"][uid] = gid
    _save_all(data)
    return gid


def get_group_members(user_id: int) -> list:
    """Lista de user_id ai membrilor din grupul curent."""
    data = _load_all()
    gid = data.get("users", {}).get(str(user_id))
    if not gid:
        return [user_id]
    return data.get("groups", {}).get(gid, {}).get("members", [user_id])


def get_group_owner(user_id: int) -> int:
    data = _load_all()
    gid = data.get("users", {}).get(str(user_id), str(user_id))
    return data.get("groups", {}).get(gid, {}).get("owner", user_id)


def is_in_shared_group(user_id: int) -> bool:
    """True dacă userul face parte dintr-un grup cu mai mulți membri."""
    return len(get_group_members(user_id)) > 1


def generate_invite_code(user_id: int) -> str:
    """Generează (sau returnează) codul de invitație al grupului."""
    data = _load_all()
    uid = str(user_id)
    _ensure_personal_group(data, user_id)
    data["users"].setdefault(uid, uid)
    gid = data["users"][uid]
    group = data["groups"][gid]

    if not group.get("invite_code"):
        # Generăm un cod unic de 6 caractere
        existing_codes = {
            g.get("invite_code") for g in data["groups"].values()
        }
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if code not in existing_codes:
                break
        group["invite_code"] = code
        _save_all(data)

    return group["invite_code"]


def join_group_by_code(user_id: int, code: str) -> tuple:
    """
    Adaugă userul la grupul cu codul dat.
    Returnează (True, group_owner_id) sau (False, mesaj_eroare).
    """
    data = _load_all()
    code = code.strip().upper()

    # Găsim grupul cu acest cod
    target_gid = None
    for gid, group in data.get("groups", {}).items():
        if group.get("invite_code") == code:
            target_gid = gid
            break

    if not target_gid:
        return False, "Cod invalid. Verifică codul și încearcă din nou."

    uid = str(user_id)
    current_gid = data.get("users", {}).get(uid)

    if current_gid == target_gid:
        return False, "Ești deja în acest grup."

    # Asigurăm că grupul personal există (pentru leave ulterior)
    _ensure_personal_group(data, user_id)

    # Adăugăm userul la grupul țintă
    group = data["groups"][target_gid]
    if user_id not in group["members"]:
        group["members"].append(user_id)

    data["users"][uid] = target_gid
    _save_all(data)
    return True, group["owner"]


def leave_group(user_id: int) -> bool:
    """Scoate userul din grupul partajat, îl pune înapoi pe grupul personal."""
    data = _load_all()
    uid = str(user_id)
    gid = data.get("users", {}).get(uid, uid)

    if gid == uid:
        return False  # deja pe grupul personal

    # Scoatem din members
    group = data["groups"].get(gid, {})
    members = group.get("members", [])
    if user_id in members:
        members.remove(user_id)

    # Restaurăm grupul personal
    _ensure_personal_group(data, user_id)
    data["users"][uid] = uid
    _save_all(data)
    return True


# ---------------------------------------------------------------------------
# Funcții helper interne pentru grupuri
# ---------------------------------------------------------------------------

def _get_group(user_id: int):
    """Returnează (all_data, group_data) pentru userul dat."""
    data = _load_all()
    uid = str(user_id)
    _ensure_personal_group(data, user_id)
    data["users"].setdefault(uid, uid)
    gid = data["users"][uid]
    return data, data["groups"][gid]


def _push_history(group: dict, entry: dict) -> None:
    history = group.setdefault("history", [])
    history.append(entry)
    if len(history) > MAX_HISTORY:
        group["history"] = history[-MAX_HISTORY:]


# ---------------------------------------------------------------------------
# API public — operații pe listă
# ---------------------------------------------------------------------------

def get_items(user_id: int) -> list:
    _, group = _get_group(user_id)
    return group["items"]


def add_item(user_id: int, name: str, category: str = DEFAULT_CATEGORY) -> dict:
    data, group = _get_group(user_id)
    uid = group.get("next_uid", 1)
    item = {"uid": uid, "name": name, "category": category, "done": False}
    group["items"].append(item)
    group["next_uid"] = uid + 1
    _push_history(group, {"action": "add", "uid": uid})
    _save_all(data)
    return item


def toggle_done(user_id: int, index: int):
    data, group = _get_group(user_id)
    items = group["items"]
    if index < 1 or index > len(items):
        return None
    item = items[index - 1]
    old_done = item["done"]
    item["done"] = not old_done
    _push_history(group, {"action": "toggle", "uid": item["uid"], "old_done": old_done})
    _save_all(data)
    return item


def remove_item(user_id: int, index: int):
    data, group = _get_group(user_id)
    items = group["items"]
    if index < 1 or index > len(items):
        return None
    removed = items.pop(index - 1)
    _push_history(group, {"action": "remove", "item": removed.copy(), "index": index - 1})
    _save_all(data)
    return removed


def clear_items(user_id: int) -> int:
    data, group = _get_group(user_id)
    count = len(group["items"])
    _push_history(group, {"action": "clear", "items": group["items"].copy()})
    group["items"] = []
    _save_all(data)
    return count


def mark_all_done(user_id: int) -> int:
    data, group = _get_group(user_id)
    old_states = {item["uid"]: item["done"] for item in group["items"]}
    count = sum(1 for i in group["items"] if not i["done"])
    for item in group["items"]:
        item["done"] = True
    if count > 0:
        _push_history(group, {"action": "mark_all", "old_states": old_states})
        _save_all(data)
    return count


def undo(user_id: int):
    data, group = _get_group(user_id)
    history = group.get("history", [])
    if not history:
        return None
    last = history.pop()
    msg = _apply_undo(group, last)
    _save_all(data)
    return msg


def _apply_undo(group: dict, entry: dict) -> str:
    items = group["items"]
    action = entry["action"]

    if action == "add":
        uid = entry["uid"]
        name = next((i["name"] for i in items if i["uid"] == uid), "?")
        group["items"] = [i for i in items if i["uid"] != uid]
        return 'Anulat: adăugare "' + name + '"'

    if action == "remove":
        idx = min(entry["index"], len(items))
        items.insert(idx, entry["item"])
        return 'Anulat: ștergere "' + entry["item"]["name"] + '"'

    if action == "toggle":
        for item in items:
            if item["uid"] == entry["uid"]:
                item["done"] = entry["old_done"]
                verb = "bifat" if not entry["old_done"] else "debifat"
                return f'Anulat: {verb} "{item["name"]}"'
        return "Anulat: bifare (produsul nu mai există)"

    if action == "clear":
        group["items"] = entry["items"]
        return f"Anulat: golire ({len(entry['items'])} produse restaurate)"

    if action == "mark_all":
        for item in items:
            if item["uid"] in entry["old_states"]:
                item["done"] = entry["old_states"][item["uid"]]
        return "Anulat: marcare toate ca cumpărate"

    return "Acțiune necunoscută"
