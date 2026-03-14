from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.enums import RoomRoleType


class RoomRoleUpdateRequest(BaseModel):
    role: RoomRoleType


class RoomRoleResponse(BaseModel):
    room_id: int
    user_id: int
    role: RoomRoleType
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomRoleListResponse(BaseModel):
    room_id: int
    roles: list[RoomRoleResponse]
