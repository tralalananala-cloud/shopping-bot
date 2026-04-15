"""Router /api/feed — feed de activitate (personal + grupuri)."""

from typing import List

from fastapi import APIRouter, Depends

import database.groups as db_groups
from api.auth import get_current_user
from api.schemas import FeedItemOut

router = APIRouter()


@router.get("/", response_model=List[FeedItemOut], summary="Feed de activitate")
async def get_feed(user_id: int = Depends(get_current_user)):
    rows = await db_groups.get_feed(user_id)
    result = []
    for r in rows:
        priority_val = 2
        try:
            priority_val = r["priority"]
        except (KeyError, IndexError):
            pass
        result.append({
            "source":       r["source"],
            "group_id":     r["group_id"],
            "group_name":   r["group_name"],
            "added_by_name": r["added_by_name"],
            "id":           r["id"],
            "item":         r["item"],
            "quantity":     r["quantity"],
            "priority":     priority_val,
            "checked":      bool(r["checked"]),
            "created_at":   str(r["created_at"]) if r["created_at"] else None,
        })
    return result
