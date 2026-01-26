from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timezone

from app.db.models import User
from app.db.enums import AuthProvider, RC, UserStatus
from app.core.security import create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def get_user_info(self, provider: str, client: Any, token: Dict) -> Dict:
        if provider == "google":
            user_info = token.get("userinfo") or await client.userinfo(token=token)
            return {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "nickname": user_info.get("name")
            }

        # TODO: 다른 프로바이더 (NAVER, KAKAO) 도 균일한 정보를 리턴하도록 분기처리

        return {}

    async def login(self, provider: str, user_data: Dict) -> str:

        email = user_data.get("email")
        if not email:
            raise ValueError("Email not found.")

        auth_provider = AuthProvider[provider.upper()]
        user = self.db.query(User).filter(
            User.email == email,
            User.auth_provider == auth_provider
        ).first()

        if not user:
            user = User(
                email=email,
                nickname=user_data.get("nickname"),
                real_name=user_data.get("name"),
                auth_provider=auth_provider,
                rc=RC.Torrey,
                status=UserStatus.ACTIVE
            )
            self.db.add(user)
        else:
            user.last_login_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(user)

        return create_access_token(subject=user.id)
