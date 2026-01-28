from sqlalchemy.orm import Session

from app.db.models import User
from app.db.enums import RC, UserStatus
from app.schemas.user import InitializeUserInfo


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_user_rc(self, user: User, new_rc: RC) -> User:
        user.rc = new_rc
        self.db.commit()
        self.db.refresh(user)
        return user

    def initialize_user_info(self, user: User, init_data: InitializeUserInfo) -> User:
        # 필드 업데이트 (UNASSIGNED → 실제 RC)
        user.rc = init_data.rc  # 필수 필드이므로 항상 업데이트
        if init_data.student_id is not None:
            user.student_id = init_data.student_id
        if init_data.major is not None:
            user.major = init_data.major
        if init_data.phone_number is not None:
            user.phone_number = init_data.phone_number
        if init_data.instagram_id is not None:
            user.instagram_id = init_data.instagram_id
        if init_data.mbti is not None:
            user.mbti = init_data.mbti

        # NEW → ACTIVE로 변경
        user.status = UserStatus.ACTIVE

        self.db.commit()
        self.db.refresh(user)
        return user
