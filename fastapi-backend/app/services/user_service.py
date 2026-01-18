from sqlalchemy.orm import Session

from app.db.models import User
from app.db.enums import RC


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_user_rc(self, user: User, new_rc: RC) -> User:
        user.rc = new_rc
        self.db.commit()
        self.db.refresh(user)
        return user
