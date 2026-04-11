"""Router /api/users — profil utilizator."""

from fastapi import APIRouter, Depends, HTTPException, status

import database.users as db_users
from api.auth import get_current_user
from api.schemas import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut, summary="Profil utilizator curent")
async def get_me(user_id: int = Depends(get_current_user)):
    user = await db_users.get_user(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Utilizatorul nu există")
    return {
        "user_id":    user["user_id"],
        "username":   user["username"],
        "first_name": user["first_name"],
        "created_at": str(user["created_at"]) if user["created_at"] else None,
    }
