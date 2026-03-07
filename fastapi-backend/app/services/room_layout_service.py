from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.enums import OwnerType
from app.db.models import Room, RoomObject, RoomPortal, RoomTile, User
from app.schemas.room_layout import (
    ReplaceObjectsRequest,
    ReplacePortalsRequest,
    ReplaceTilesRequest,
    RoomLayoutResponse,
    RoomObjectPayload,
    RoomPortalPayload,
    RoomTilePayload,
)


class RoomLayoutService:
    def __init__(self, db: Session):
        self.db = db

    def _get_room(self, room_id: int) -> Room:
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")
        return room

    def _ensure_user_can_edit(self, room: Room, user: User) -> None:
        if room.owner_type != OwnerType.USER or room.owner_id != user.id:
            raise HTTPException(status_code=403, detail="No permission to edit this room")

    def _ensure_user_can_read(self, room: Room, user: User) -> None:
        if room.is_public:
            return
        if room.owner_type == OwnerType.USER and room.owner_id == user.id:
            return
        raise HTTPException(status_code=403, detail="No permission to read this room")

    def _touch_room(self, room: Room) -> None:
        room.updated_at = datetime.now(timezone.utc)

    def get_layout(self, room_id: int, user: User) -> RoomLayoutResponse:
        room = self._get_room(room_id)
        self._ensure_user_can_read(room, user)

        tiles = self.db.query(RoomTile).filter(RoomTile.room_id == room_id).all()
        objects = self.db.query(RoomObject).filter(RoomObject.room_id == room_id).all()
        portals = self.db.query(RoomPortal).filter(RoomPortal.from_room_id == room_id).all()

        return RoomLayoutResponse(
            room_id=room.id,
            width=room.width,
            height=room.height,
            tiles=[
                RoomTilePayload(x=t.x, y=t.y, tile_asset_id=t.tile_asset_id)
                for t in tiles
            ],
            objects=[
                RoomObjectPayload(x=o.x, y=o.y, object_asset_id=o.object_asset_id)
                for o in objects
            ],
            portals=[
                RoomPortalPayload(from_x=p.from_x, from_y=p.from_y, to_room_id=p.to_room_id)
                for p in portals
            ],
        )

    def replace_tiles(
        self, room_id: int, user: User, request_data: ReplaceTilesRequest
    ) -> list[RoomTilePayload]:
        room = self._get_room(room_id)
        self._ensure_user_can_edit(room, user)

        visited: set[tuple[int, int]] = set()
        for tile in request_data.tiles:
            if tile.x >= room.width or tile.y >= room.height:
                raise HTTPException(status_code=400, detail="Tile coordinates out of room bounds")
            pos = (tile.x, tile.y)
            if pos in visited:
                raise HTTPException(status_code=400, detail="Duplicate tile coordinates")
            visited.add(pos)

        self.db.query(RoomTile).filter(RoomTile.room_id == room_id).delete(synchronize_session=False)
        for tile in request_data.tiles:
            self.db.add(
                RoomTile(
                    room_id=room_id,
                    x=tile.x,
                    y=tile.y,
                    tile_asset_id=tile.tile_asset_id,
                )
            )

        self._touch_room(room)
        self.db.commit()

        return request_data.tiles

    def replace_objects(
        self, room_id: int, user: User, request_data: ReplaceObjectsRequest
    ) -> list[RoomObjectPayload]:
        room = self._get_room(room_id)
        self._ensure_user_can_edit(room, user)

        visited: set[tuple[int, int]] = set()
        for obj in request_data.objects:
            if obj.x >= room.width or obj.y >= room.height:
                raise HTTPException(status_code=400, detail="Object coordinates out of room bounds")
            pos = (obj.x, obj.y)
            if pos in visited:
                raise HTTPException(status_code=400, detail="Duplicate object coordinates")
            visited.add(pos)

        self.db.query(RoomObject).filter(RoomObject.room_id == room_id).delete(synchronize_session=False)
        for obj in request_data.objects:
            self.db.add(
                RoomObject(
                    room_id=room_id,
                    x=obj.x,
                    y=obj.y,
                    object_asset_id=obj.object_asset_id,
                )
            )

        self._touch_room(room)
        self.db.commit()

        return request_data.objects

    def replace_portals(
        self, room_id: int, user: User, request_data: ReplacePortalsRequest
    ) -> list[RoomPortalPayload]:
        room = self._get_room(room_id)
        self._ensure_user_can_edit(room, user)

        visited: set[tuple[int, int]] = set()
        target_room_ids = {portal.to_room_id for portal in request_data.portals}
        if target_room_ids:
            existing_target_ids = {
                r.id for r in self.db.query(Room).filter(Room.id.in_(target_room_ids)).all()
            }
            missing = target_room_ids - existing_target_ids
            if missing:
                raise HTTPException(status_code=400, detail=f"Invalid target room ids: {sorted(missing)}")

        for portal in request_data.portals:
            if portal.from_x >= room.width or portal.from_y >= room.height:
                raise HTTPException(status_code=400, detail="Portal coordinates out of room bounds")
            pos = (portal.from_x, portal.from_y)
            if pos in visited:
                raise HTTPException(status_code=400, detail="Duplicate portal coordinates")
            visited.add(pos)

        self.db.query(RoomPortal).filter(RoomPortal.from_room_id == room_id).delete(
            synchronize_session=False
        )
        for portal in request_data.portals:
            self.db.add(
                RoomPortal(
                    from_room_id=room_id,
                    from_x=portal.from_x,
                    from_y=portal.from_y,
                    to_room_id=portal.to_room_id,
                )
            )

        self._touch_room(room)
        self.db.commit()

        return request_data.portals
