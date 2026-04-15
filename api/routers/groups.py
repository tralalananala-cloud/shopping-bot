"""Router /api/groups — grupuri partajate de cumpărături."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

import database.groups as db_groups
import database.users as db_users
from api.auth import get_current_user
from api.notifications import notify_item_added, notify_item_checked
from api.schemas import (
    CountResponse,
    GroupCreate,
    GroupItemCreate,
    GroupItemOut,
    GroupJoin,
    GroupListOut,
    GroupOut,
    GroupRename,
    GroupsListOut,
    MemberOut,
    MembersListOut,
    OkResponse,
)
from utils.helpers import parse_item_input

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers de conversie
# ---------------------------------------------------------------------------

async def _group_out(row) -> dict:
    cnt = await db_groups.member_count(row["id"])
    return {
        "id":           row["id"],
        "name":         row["name"],
        "owner_id":     row["owner_id"],
        "invite_code":  row["invite_code"],
        "created_at":   str(row["created_at"]) if row["created_at"] else None,
        "member_count": cnt,
    }


def _item_out(row) -> dict:
    adder = row["first_name"] or row["username"] or f"User #{row['added_by']}"
    priority_val = 2
    try:
        priority_val = row["priority"]
    except (KeyError, IndexError):
        pass
    return {
        "id":            row["id"],
        "group_id":      row["group_id"],
        "item":          row["item"],
        "quantity":      row["quantity"],
        "priority":      priority_val,
        "checked":       bool(row["checked"]),
        "added_by":      row["added_by"],
        "added_by_name": adder,
        "created_at":    str(row["created_at"]) if row["created_at"] else None,
    }


def _member_out(row, owner_id: int) -> dict:
    return {
        "user_id":    row["user_id"],
        "username":   row["username"],
        "first_name": row["first_name"],
        "joined_at":  str(row["joined_at"]) if row["joined_at"] else None,
        "is_owner":   row["user_id"] == owner_id,
    }


async def _actor_name(user_id: int) -> str:
    user = await db_users.get_user(user_id)
    if user:
        return user["first_name"] or user["username"] or f"User #{user_id}"
    return f"User #{user_id}"


# ---------------------------------------------------------------------------
# GET /api/groups/
# ---------------------------------------------------------------------------

@router.get("/", response_model=GroupsListOut, summary="Grupurile mele")
async def get_my_groups(user_id: int = Depends(get_current_user)):
    rows = await db_groups.get_user_groups(user_id)
    groups = []
    for r in rows:
        groups.append(await _group_out(r))
    return {"groups": groups}


# ---------------------------------------------------------------------------
# POST /api/groups/
# ---------------------------------------------------------------------------

@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED,
             summary="Creează grup nou")
async def create_group(
    body: GroupCreate,
    user_id: int = Depends(get_current_user),
):
    name = body.name.strip()
    if not name:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Numele grupului nu poate fi gol")
    if len(name) > 50:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Numele e prea lung (max 50 caractere)")

    group_id = await db_groups.create_group(name, user_id)
    row = await db_groups.get_group(group_id)
    return await _group_out(row)


# ---------------------------------------------------------------------------
# POST /api/groups/join
# ---------------------------------------------------------------------------

@router.post("/join", response_model=GroupOut, summary="Alătură-te la un grup cu cod de invitație")
async def join_group(
    body: GroupJoin,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group_by_code(body.invite_code.strip().upper())
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cod de invitație inexistent")

    if await db_groups.is_member(group["id"], user_id):
        return await _group_out(group)

    await db_groups.add_member(group["id"], user_id)
    row = await db_groups.get_group(group["id"])
    return await _group_out(row)


# ---------------------------------------------------------------------------
# GET /api/groups/{group_id}
# ---------------------------------------------------------------------------

@router.get("/{group_id}", response_model=GroupListOut, summary="Lista produselor din grup")
async def get_group(
    group_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu ești membru al acestui grup")

    rows  = await db_groups.get_group_items(group_id)
    items = [_item_out(r) for r in rows]
    done  = sum(1 for i in items if i["checked"])
    return {
        "group": await _group_out(group),
        "items": items,
        "total": len(items),
        "done":  done,
    }


# ---------------------------------------------------------------------------
# POST /api/groups/{group_id}/items
# ---------------------------------------------------------------------------

@router.post("/{group_id}/items", response_model=GroupItemOut,
             status_code=status.HTTP_201_CREATED, summary="Adaugă produs în grup")
async def add_group_item(
    group_id: int,
    body: GroupItemCreate,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu ești membru al acestui grup")

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

    item_id = await db_groups.add_group_item(group_id, item_name, qty, user_id, priority)
    rows = await db_groups.get_group_items(group_id)
    row  = next((r for r in rows if r["id"] == item_id), None)
    if not row:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Eroare la salvarea produsului")

    # Trimite notificări
    try:
        actor = await _actor_name(user_id)
        member_ids = await db_groups.get_member_ids(group_id)
        await notify_item_added(actor, item_name, group["name"], member_ids, user_id)
    except Exception:
        pass

    return _item_out(row)


# ---------------------------------------------------------------------------
# PATCH /api/groups/{group_id}/items/{item_id}/toggle
# ---------------------------------------------------------------------------

@router.patch("/{group_id}/items/{item_id}/toggle", response_model=GroupItemOut,
              summary="Bifează/debifează produs din grup")
async def toggle_group_item(
    group_id: int,
    item_id: int,
    user_id: int = Depends(get_current_user),
):
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu ești membru al acestui grup")

    row = await db_groups.get_group_item(item_id, group_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produsul nu există")

    item_name_before = row["item"]
    was_checked = bool(row["checked"])

    new_state = await db_groups.toggle_group_item(item_id, group_id)

    rows = await db_groups.get_group_items(group_id)
    updated = next((r for r in rows if r["id"] == item_id), None)
    if not updated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produsul nu mai există")

    # Trimite notificare doar când produsul e bifat (nu la debifat)
    if new_state and not was_checked:
        try:
            group = await db_groups.get_group(group_id)
            actor = await _actor_name(user_id)
            member_ids = await db_groups.get_member_ids(group_id)
            await notify_item_checked(actor, item_name_before, group["name"], member_ids, user_id)
        except Exception:
            pass

    return _item_out(updated)


# ---------------------------------------------------------------------------
# DELETE /api/groups/{group_id}/items/{item_id}
# ---------------------------------------------------------------------------

@router.delete("/{group_id}/items/{item_id}", response_model=OkResponse,
               summary="Șterge produs din grup")
async def delete_group_item(
    group_id: int,
    item_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu ești membru al acestui grup")

    row = await db_groups.get_group_item(item_id, group_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produsul nu există")

    if row["added_by"] != user_id and group["owner_id"] != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu poți șterge produsul altcuiva")

    await db_groups.delete_group_item(item_id, group_id)
    return {"ok": True}


# ---------------------------------------------------------------------------
# DELETE /api/groups/{group_id}/items/clear/checked
# ---------------------------------------------------------------------------

@router.delete("/{group_id}/items/clear/checked", response_model=CountResponse,
               summary="Șterge toate produsele bifate din grup")
async def clear_group_checked(
    group_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu ești membru al acestui grup")

    count = await db_groups.clear_group_checked(group_id)
    return {"ok": True, "count": count}


# ---------------------------------------------------------------------------
# GET /api/groups/{group_id}/members
# ---------------------------------------------------------------------------

@router.get("/{group_id}/members", response_model=MembersListOut, summary="Membrii grupului")
async def get_members(
    group_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Nu ești membru al acestui grup")

    rows = await db_groups.get_members(group_id)
    members = [_member_out(r, group["owner_id"]) for r in rows]
    return {"group_id": group_id, "members": members}


# ---------------------------------------------------------------------------
# DELETE /api/groups/{group_id}/members/{target_id}  (kick — doar owner)
# ---------------------------------------------------------------------------

@router.delete("/{group_id}/members/{target_id}", response_model=OkResponse,
               summary="Elimină un membru (doar owner)")
async def kick_member(
    group_id: int,
    target_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if group["owner_id"] != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Doar owner-ul poate elimina membri")
    if target_id == user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Nu te poți elimina pe tine însuți")

    await db_groups.remove_member(group_id, target_id)
    return {"ok": True}


# ---------------------------------------------------------------------------
# DELETE /api/groups/{group_id}/leave
# ---------------------------------------------------------------------------

@router.delete("/{group_id}/leave", response_model=OkResponse, summary="Ieși din grup")
async def leave_group(
    group_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if group["owner_id"] == user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail="Owner-ul nu poate ieși din grup. Șterge grupul sau transferă ownership-ul.")
    if not await db_groups.is_member(group_id, user_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Nu ești în acest grup")

    await db_groups.remove_member(group_id, user_id)
    return {"ok": True}


# ---------------------------------------------------------------------------
# PATCH /api/groups/{group_id}/rename  (doar owner)
# ---------------------------------------------------------------------------

@router.patch("/{group_id}/rename", response_model=GroupOut, summary="Redenumește grup (doar owner)")
async def rename_group(
    group_id: int,
    body: GroupRename,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if group["owner_id"] != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Doar owner-ul poate redenumi grupul")

    name = body.name.strip()
    if not name:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Numele nu poate fi gol")
    if len(name) > 50:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Numele e prea lung (max 50 caractere)")

    await db_groups.rename_group(group_id, name)
    row = await db_groups.get_group(group_id)
    return await _group_out(row)


# ---------------------------------------------------------------------------
# DELETE /api/groups/{group_id}  (doar owner)
# ---------------------------------------------------------------------------

@router.delete("/{group_id}", response_model=OkResponse, summary="Șterge grup (doar owner)")
async def delete_group(
    group_id: int,
    user_id: int = Depends(get_current_user),
):
    group = await db_groups.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grupul nu există")
    if group["owner_id"] != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Doar owner-ul poate șterge grupul")

    await db_groups.delete_group(group_id)
    return {"ok": True}
