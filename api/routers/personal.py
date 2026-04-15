"""Router /api/personal — lista personală de cumpărături."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

import database.personal as db_personal
from api.auth import get_current_user
from api.schemas import (
    CountResponse,
    OkResponse,
    PersonalItemCreate,
    PersonalItemOut,
    PersonalListOut,
)
from utils.helpers import parse_item_input

router = APIRouter()


def _item_to_dict(row) -> dict:
    return {
        "id":         row["id"],
        "user_id":    row["user_id"],
        "item":       row["item"],
        "quantity":   row["quantity"],
        "priority":   row.get("priority", 2) if hasattr(row, "get") else (row["priority"] if "priority" in row.keys() else 2),
        "checked":    bool(row["checked"]),
        "created_at": str(row["created_at"]) if row["created_at"] else None,
    }


# ---------------------------------------------------------------------------
# GET /api/personal/
# ---------------------------------------------------------------------------

@router.get("/", response_model=PersonalListOut, summary="Lista personală")
async def get_personal_list(user_id: int = Depends(get_current_user)):
    rows = await db_personal.get_items(user_id)
    items = [_item_to_dict(r) for r in rows]
    done  = sum(1 for i in items if i["checked"])
    return {"items": items, "total": len(items), "done": done}


# ---------------------------------------------------------------------------
# POST /api/personal/
# ---------------------------------------------------------------------------

@router.post("/", response_model=PersonalItemOut, status_code=status.HTTP_201_CREATED,
             summary="Adaugă produs")
async def add_personal_item(
    body: PersonalItemCreate,
    user_id: int = Depends(get_current_user),
):
    text = body.item.strip()
    if not text:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Produsul nu poate fi gol")
    if len(text) > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Produsul e prea lung (max 200 caractere)")

    priority = max(1, min(3, body.priority))

    if body.quantity == "1":
        item_name, qty = parse_item_input(text)
    else:
        item_name, qty = text, body.quantity

    item_id = await db_personal.add_item(user_id, item_name, qty, priority)
    row = await db_personal.get_item(item_id, user_id)
    return _item_to_dict(row)


# ---------------------------------------------------------------------------
# PATCH /api/personal/{item_id}/toggle
# ---------------------------------------------------------------------------

@router.patch("/{item_id}/toggle", response_model=PersonalItemOut, summary="Bifează/debifează produs")
async def toggle_personal_item(
    item_id: int,
    user_id: int = Depends(get_current_user),
):
    row = await db_personal.get_item(item_id, user_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produsul nu există")
    await db_personal.toggle_item(item_id, user_id)
    row = await db_personal.get_item(item_id, user_id)
    return _item_to_dict(row)


# ---------------------------------------------------------------------------
# DELETE /api/personal/{item_id}
# ---------------------------------------------------------------------------

@router.delete("/{item_id}", response_model=OkResponse, summary="Șterge produs")
async def delete_personal_item(
    item_id: int,
    user_id: int = Depends(get_current_user),
):
    deleted = await db_personal.delete_item(item_id, user_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produsul nu există")
    return {"ok": True}


# ---------------------------------------------------------------------------
# DELETE /api/personal/clear/checked
# ---------------------------------------------------------------------------

@router.delete("/clear/checked", response_model=CountResponse, summary="Șterge toate produsele bifate")
async def clear_personal_checked(user_id: int = Depends(get_current_user)):
    count = await db_personal.clear_checked(user_id)
    return {"ok": True, "count": count}
