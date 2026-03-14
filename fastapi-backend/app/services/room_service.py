import hashlib

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.enums import OwnerType
from app.db.models import Room, User
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
# 룸 생성, 조회, 수정 등의 비즈니스 로직을 담당하는 서비스 클래스
    def __init__(self, db: Session):
        self.db = db

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _ensure_user_can_edit(self, room: Room, user: User) -> None:
        if room.owner_type != OwnerType.USER or room.owner_id != user.id:
            raise HTTPException(status_code=403, detail="No permission to edit this room")

    def _ensure_user_can_read(self, room: Room, user: User) -> None:
        if room.is_public:
            return
        if room.owner_type == OwnerType.USER and room.owner_id == user.id:
            return
        raise HTTPException(status_code=403, detail="No permission to read this room")

    def create_room(self, user: User, room_data: RoomCreate) -> Room:
        if room_data.owner_type != OwnerType.USER:
            raise HTTPException(status_code=400, detail="Only USER owner type is supported now")

        password_hash = None
        if not room_data.is_public and room_data.password:
            password_hash = self._hash_password(room_data.password)

        room = Room(
            room_type=room_data.room_type,
            name=room_data.name,
            owner_type=OwnerType.USER,
            owner_id=user.id,
            is_public=room_data.is_public,
            password_hash=password_hash,
            width=room_data.width,
            height=room_data.height,
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def get_room(self, room_id: int, user: User) -> Room:
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        self._ensure_user_can_read(room, user)
        return room

    def list_rooms(
        self, user: User, limit: int = 20, offset: int = 0, mine_only: bool = False
    ) -> tuple[int, list[Room]]:
        query = self.db.query(Room)

        if mine_only:
            query = query.filter(Room.owner_type == OwnerType.USER, Room.owner_id == user.id)
        else:
            query = query.filter(
                or_(
                    Room.is_public.is_(True),
                    (Room.owner_type == OwnerType.USER) & (Room.owner_id == user.id),
                )
            )

        total = query.count()
        rooms = query.order_by(Room.updated_at.desc()).offset(offset).limit(limit).all()
        return total, rooms

    def update_room(self, room_id: int, user: User, room_data: RoomUpdate) -> Room:
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        self._ensure_user_can_edit(room, user)

        if room_data.name is not None:
            room.name = room_data.name
        if room_data.width is not None:
            room.width = room_data.width
        if room_data.height is not None:
            room.height = room_data.height
        if room_data.is_public is not None:
            room.is_public = room_data.is_public
            if room.is_public:
                room.password_hash = None
        if room_data.password is not None:
            room.password_hash = self._hash_password(room_data.password)

        self.db.commit()
        self.db.refresh(room)
        return room
