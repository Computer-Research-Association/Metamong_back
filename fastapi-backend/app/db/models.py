from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Enum, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

from app.db.enums import AuthProvider, RC, UserStatus, RoomType, OwnerType


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=True)
    nickname = Column(String(50), nullable=False)
    real_name = Column(String(50), nullable=False)

    password_hash = Column(String(255))
    auth_provider = Column(Enum(AuthProvider), nullable=False)

    rc = Column(Enum(RC), nullable=False)
    status = Column(Enum(UserStatus), nullable=False,
                    default=UserStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))

    last_room_id = Column(BigInteger, ForeignKey("rooms.id"))
    last_room_x = Column(Integer)
    last_room_y = Column(Integer)

    owned_teams = relationship("Team", back_populates="owner")


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
    room_type = Column(Enum(RoomType), nullable=False)
    name = Column(String(50), nullable=False)

    owner_type = Column(Enum(OwnerType), nullable=False)
    owner_id = Column(BigInteger)

    is_public = Column(Boolean, nullable=False, default=False)
    password_hash = Column(String(255))

    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
