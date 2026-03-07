from typing import List

from pydantic import BaseModel, Field


class RoomTilePayload(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    tile_asset_id: int


class RoomObjectPayload(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    object_asset_id: str = Field(min_length=1, max_length=100)


class RoomPortalPayload(BaseModel):
    from_x: int = Field(ge=0)
    from_y: int = Field(ge=0)
    to_room_id: int


class GridPosition(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class PortalPosition(BaseModel):
    from_x: int = Field(ge=0)
    from_y: int = Field(ge=0)


class ReplaceTilesRequest(BaseModel):
    tiles: List[RoomTilePayload]


class ReplaceObjectsRequest(BaseModel):
    objects: List[RoomObjectPayload]


class ReplacePortalsRequest(BaseModel):
    portals: List[RoomPortalPayload]


class PatchTilesRequest(BaseModel):
    upserts: List[RoomTilePayload] = Field(default_factory=list)
    removes: List[GridPosition] = Field(default_factory=list)


class PatchObjectsRequest(BaseModel):
    upserts: List[RoomObjectPayload] = Field(default_factory=list)
    removes: List[GridPosition] = Field(default_factory=list)


class PatchPortalsRequest(BaseModel):
    upserts: List[RoomPortalPayload] = Field(default_factory=list)
    removes: List[PortalPosition] = Field(default_factory=list)


class RoomLayoutResponse(BaseModel):
    room_id: int
    width: int
    height: int
    tiles: List[RoomTilePayload]
    objects: List[RoomObjectPayload]
    portals: List[RoomPortalPayload]


class ReplaceTilesResponse(BaseModel):
    room_id: int
    tiles: List[RoomTilePayload]


class ReplaceObjectsResponse(BaseModel):
    room_id: int
    objects: List[RoomObjectPayload]


class ReplacePortalsResponse(BaseModel):
    room_id: int
    portals: List[RoomPortalPayload]


class PatchTilesResponse(BaseModel):
    room_id: int
    tiles: List[RoomTilePayload]


class PatchObjectsResponse(BaseModel):
    room_id: int
    objects: List[RoomObjectPayload]


class PatchPortalsResponse(BaseModel):
    room_id: int
    portals: List[RoomPortalPayload]
