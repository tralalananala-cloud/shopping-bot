"""
Modele Pydantic pentru request/response API.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserOut(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Lista personală
# ---------------------------------------------------------------------------

class PersonalItemCreate(BaseModel):
    item: str
    quantity: str = "1"
    priority: int = 2  # 1=mică, 2=normală, 3=mare


class PersonalItemOut(BaseModel):
    id: int
    user_id: int
    item: str
    quantity: str
    priority: int = 2
    checked: bool
    created_at: Optional[str] = None


class PersonalListOut(BaseModel):
    items: List[PersonalItemOut]
    total: int
    done: int


# ---------------------------------------------------------------------------
# Grupuri
# ---------------------------------------------------------------------------

class GroupCreate(BaseModel):
    name: str


class GroupJoin(BaseModel):
    invite_code: str


class GroupRename(BaseModel):
    name: str


class GroupOut(BaseModel):
    id: int
    name: str
    owner_id: int
    invite_code: str
    created_at: Optional[str] = None
    member_count: Optional[int] = None


class GroupsListOut(BaseModel):
    groups: List[GroupOut]


# ---------------------------------------------------------------------------
# Lista grupului
# ---------------------------------------------------------------------------

class GroupItemCreate(BaseModel):
    item: str
    quantity: str = "1"
    priority: int = 2  # 1=mică, 2=normală, 3=mare


class GroupItemOut(BaseModel):
    id: int
    group_id: int
    item: str
    quantity: str
    priority: int = 2
    checked: bool
    added_by: int
    added_by_name: Optional[str] = None
    created_at: Optional[str] = None


class GroupListOut(BaseModel):
    group: GroupOut
    items: List[GroupItemOut]
    total: int
    done: int


# ---------------------------------------------------------------------------
# Membri
# ---------------------------------------------------------------------------

class MemberOut(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    joined_at: Optional[str] = None
    is_owner: bool = False


class MembersListOut(BaseModel):
    group_id: int
    members: List[MemberOut]


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------

class FeedItemOut(BaseModel):
    source: Literal["personal", "group"]
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    added_by_name: str
    id: int
    item: str
    quantity: str
    priority: int = 2
    checked: bool
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Răspunsuri generice
# ---------------------------------------------------------------------------

class OkResponse(BaseModel):
    ok: bool = True
    message: Optional[str] = None


class CountResponse(BaseModel):
    ok: bool = True
    count: int
