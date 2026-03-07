from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.enums import RoomType, OwnerType


class RoomCreate(BaseModel):
    room_type: RoomType
    name: str = Field(min_length=1, max_length=50)
    owner_type: OwnerType = OwnerType.USER
    is_public: bool = False
    password: Optional[str] = Field(default=None, min_length=1, max_length=255)
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    is_public: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=1, max_length=255)
    width: Optional[int] = Field(default=None, ge=1)
    height: Optional[int] = Field(default=None, ge=1)


class RoomResponse(BaseModel):
    id: int
    room_type: RoomType
    name: str
    owner_type: OwnerType
    owner_id: Optional[int]
    is_public: bool
    width: int
    height: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    rooms: list[RoomResponse]
