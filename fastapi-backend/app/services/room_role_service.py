from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.enums import OwnerType, RoomRoleType
from app.db.models import Room, RoomRole, User
from app.schemas.room_role import RoomRoleResponse


class RoomRoleService:
    def __init__(self, db: Session):
        self.db = db

    def _get_room(self, room_id: int) -> Room:
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")
        return room

    def _ensure_owner_can_manage(self, room: Room, current_user: User) -> None:
        if room.owner_type != OwnerType.USER or room.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="No permission to manage room roles")

    def _ensure_user_can_read(self, room: Room, current_user: User) -> None:
        if room.is_public:
            return
        if room.owner_type == OwnerType.USER and room.owner_id == current_user.id:
            return
        raise HTTPException(status_code=403, detail="No permission to read room roles")

    def list_roles(self, room_id: int, current_user: User) -> list[RoomRoleResponse]:
        room = self._get_room(room_id)
        self._ensure_user_can_read(room, current_user)

        roles = []
        if room.owner_type == OwnerType.USER and room.owner_id is not None:
            roles.append(
                RoomRoleResponse(
                    room_id=room.id,
                    user_id=room.owner_id,
                    role=RoomRoleType.OWNER,
                    created_at=None,
                )
            )

        role_rows = self.db.query(RoomRole).filter(RoomRole.room_id == room_id).all()
        for row in role_rows:
            if room.owner_type == OwnerType.USER and row.user_id == room.owner_id:
                continue
            roles.append(
                RoomRoleResponse(
                    room_id=row.room_id,
                    user_id=row.user_id,
                    role=row.role,
                    created_at=row.created_at,
                )
            )

        return roles

    def get_role(
        self, room_id: int, target_user_id: int, current_user: User
    ) -> RoomRoleResponse:
        room = self._get_room(room_id)
        self._ensure_user_can_read(room, current_user)

        if room.owner_type == OwnerType.USER and room.owner_id == target_user_id:
            return RoomRoleResponse(
                room_id=room.id,
                user_id=target_user_id,
                role=RoomRoleType.OWNER,
                created_at=None,
            )

        row = self.db.query(RoomRole).filter(
            RoomRole.room_id == room_id, RoomRole.user_id == target_user_id
        ).first()
        if row is None:
            return RoomRoleResponse(
                room_id=room_id,
                user_id=target_user_id,
                role=RoomRoleType.VISITOR,
                created_at=None,
            )

        return RoomRoleResponse(
            room_id=row.room_id,
            user_id=row.user_id,
            role=row.role,
            created_at=row.created_at,
        )

    def upsert_role(
        self, room_id: int, target_user_id: int, role: RoomRoleType, current_user: User
    ) -> RoomRoleResponse:
        room = self._get_room(room_id)
        self._ensure_owner_can_manage(room, current_user)

        target_user = self.db.query(User).filter(User.id == target_user_id).first()
        if target_user is None:
            raise HTTPException(status_code=404, detail="Target user not found")

        if room.owner_type == OwnerType.USER and room.owner_id == target_user_id:
            raise HTTPException(status_code=400, detail="Owner role is fixed and cannot be changed")

        if role == RoomRoleType.OWNER:
            raise HTTPException(status_code=400, detail="OWNER assignment is not supported in this API")

        if role == RoomRoleType.VISITOR:
            self.db.query(RoomRole).filter(
                RoomRole.room_id == room_id, RoomRole.user_id == target_user_id
            ).delete(synchronize_session=False)
            self.db.commit()
            return RoomRoleResponse(
                room_id=room_id,
                user_id=target_user_id,
                role=RoomRoleType.VISITOR,
                created_at=None,
            )

        row = self.db.query(RoomRole).filter(
            RoomRole.room_id == room_id, RoomRole.user_id == target_user_id
        ).first()
        if row is None:
            row = RoomRole(room_id=room_id, user_id=target_user_id, role=role)
            self.db.add(row)
        else:
            row.role = role

        self.db.commit()
        self.db.refresh(row)
        return RoomRoleResponse(
            room_id=row.room_id, user_id=row.user_id, role=row.role, created_at=row.created_at
        )
