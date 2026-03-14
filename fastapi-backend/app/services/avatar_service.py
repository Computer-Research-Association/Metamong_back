"""
Avatar 비즈니스 로직 서비스.
"""
from sqlalchemy.orm import Session

from app.db.models import Avatar, User
from app.schemas.avatar import AvatarCreate


class AvatarService:
    def __init__(self, db: Session):
        self.db = db

    def create_avatar(self, user: User, create_data: AvatarCreate) -> Avatar:
        """
        현재 유저 소유로 새 아바타를 생성합니다.

        :param user: 아바타 소유자 (현재 인증된 유저)
        :param create_data: avatar_asset_id, nickname
        :return: 생성된 Avatar 엔티티
        """
        avatar = Avatar(
            user_id=user.id,
            avatar_asset_id=create_data.avatar_asset_id.strip(),
            nickname=create_data.nickname.strip(),
        )
        self.db.add(avatar)
        self.db.commit()
        self.db.refresh(avatar)
        return avatar

    def get_avatar_by_id(self, avatar_id: int) -> Avatar | None:
        """
        Avatar id로 아바타를 조회합니다.

        :param avatar_id: 조회할 아바타 id
        :return: 있으면 Avatar, 없으면 None
        """
        return self.db.query(Avatar).filter(Avatar.id == avatar_id).first()

    def delete_avatar(self, avatar: Avatar) -> None:
        """
        아바타를 삭제합니다. 호출 전에 소유자 여부는 라우터에서 검사합니다.

        :param avatar: 삭제할 Avatar 엔티티
        """
        self.db.delete(avatar)
        self.db.commit()
