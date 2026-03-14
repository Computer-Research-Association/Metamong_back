"""
Avatar 비즈니스 로직 서비스.
"""
from sqlalchemy.orm import Session

from app.db.models import Avatar


class AvatarService:
    def __init__(self, db: Session):
        self.db = db

    def get_avatar_by_id(self, avatar_id: int) -> Avatar | None:
        """
        Avatar id로 아바타를 조회합니다.

        :param avatar_id: 조회할 아바타 id
        :return: 있으면 Avatar, 없으면 None
        """
        return self.db.query(Avatar).filter(Avatar.id == avatar_id).first()
