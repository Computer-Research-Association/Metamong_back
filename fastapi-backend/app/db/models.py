from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, DateTime, Integer, SAEnum, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.enums import AuthProvider, RC, UserStatus, RoomType, OwnerType, RoomRoleType, FriendStatus

if TYPE_CHECKING:
    from app.db.models import Team


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True)
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True)
    nickname: Mapped[str] = mapped_column(String(50))
    real_name: Mapped[str] = mapped_column(String(50))

    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(SAEnum(AuthProvider))

    rc: Mapped[RC] = mapped_column(SAEnum(RC))
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus),
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.value
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    last_login_at: Mapped[Optional[datetime]
                          ] = mapped_column(DateTime(timezone=True))

    last_room_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("rooms.id"))
    last_room_x: Mapped[Optional[int]] = mapped_column(Integer)
    last_room_y: Mapped[Optional[int]] = mapped_column(Integer)

    owned_teams: Mapped[List["Team"]] = relationship(
        "Team", back_populates="owner")


Index("idx_users_auth_provider", User.auth_provider)
Index("idx_users_last_room_id", User.last_room_id)


class Team(Base):
    __tablename__ = "teams"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    owner_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())

    owner = relationship("User", back_populates="owned_teams")


Index("idx_teams_owner_user_id", Team.owner_user_id)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_type = Column(SAEnum(RoomType), nullable=False)
    name = Column(String(50), nullable=False)

    owner_type = Column(SAEnum(OwnerType), nullable=False)
    owner_id = Column(BigInteger)

    is_public = Column(Boolean, nullable=False, default=False)
    password_hash = Column(String(255))

    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())


Index("idx_rooms_room_type", Room.room_type)
Index("idx_rooms_owner", Room.owner_type, Room.owner_id)
Index("idx_rooms_is_public", Room.is_public)


class RoomTile(Base):
    __tablename__ = "room_tiles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False)

    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    tile_asset_id = Column(BigInteger, nullable=False)

    room = relationship("Room")


Index("idx_room_tiles_room_id", RoomTile.room_id)
Index(
    "uq_room_tiles_position",
    RoomTile.room_id,
    RoomTile.x,
    RoomTile.y,
    unique=True,
)
Index("idx_room_tiles_asset", RoomTile.tile_asset_id)


class RoomObject(Base):
    __tablename__ = "room_objects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False)

    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    object_asset_id = Column(String(100), nullable=False)

    room = relationship("Room")


Index("idx_room_objects_room_id", RoomObject.room_id)
Index(
    "uq_room_objects_position",
    RoomObject.room_id,
    RoomObject.x,
    RoomObject.y,
    unique=True,
)
Index("idx_room_objects_asset", RoomObject.object_asset_id)


class RoomPortal(Base):
    __tablename__ = "room_portals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    from_room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False)
    from_x = Column(Integer, nullable=False)
    from_y = Column(Integer, nullable=False)

    to_room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False)


Index("idx_room_portals_from_room", RoomPortal.from_room_id)
Index("idx_room_portals_to_room", RoomPortal.to_room_id)
Index(
    "idx_room_portals_from_position",
    RoomPortal.from_room_id,
    RoomPortal.from_x,
    RoomPortal.from_y,
)


class RoomRole(Base):
    __tablename__ = "room_roles"

    room_id = Column(BigInteger, ForeignKey("rooms.id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)

    role = Column(SAEnum(RoomRoleType),
                  nullable=False,
                  default=RoomRoleType.VISITOR
                  )
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())


Index("idx_room_roles_user_id", RoomRole.user_id)


class Friend(Base):
    __tablename__ = "friends"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    friend_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    status = Column(SAEnum(FriendStatus), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())


Index("idx_friends_user_id", Friend.user_id)
Index("idx_friends_friend_user_id", Friend.friend_user_id)
Index(
    "uq_friends_pair",
    Friend.user_id,
    Friend.friend_user_id,
    unique=True,
)
