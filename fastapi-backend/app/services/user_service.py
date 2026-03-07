from sqlalchemy.orm import Session

from app.db.models import User
from app.db.enums import RC, UserStatus
from app.schemas.user import InitializeUserInfo, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_user(self, user: User, update_data: UserUpdate) -> User:
        if update_data.rc is not None:
            user.rc = update_data.rc
        if update_data.nickname is not None:
            user.nickname = update_data.nickname
        if update_data.real_name is not None:
            user.real_name = update_data.real_name
        if update_data.student_id is not None:
            user.student_id = update_data.student_id
        if update_data.major is not None:
            user.major = update_data.major
        if update_data.phone_number is not None:
            user.phone_number = update_data.phone_number
        if update_data.instagram_id is not None:
            user.instagram_id = update_data.instagram_id
        if update_data.mbti is not None:
            user.mbti = update_data.mbti

        if user.status == UserStatus.NEW and user.rc != RC.UNASSIGNED:
            user.status = UserStatus.ACTIVE

        self.db.commit()
        self.db.refresh(user)
        return user

    def initialize_user_info(self, user: User, init_data: InitializeUserInfo) -> User:
        # NEW 유저만 초기화 처리
        if user.status == UserStatus.NEW:
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
        
        # ACTIVE 유저는 그냥 현재 유저 정보 반환 (변경 없음)
        return user
