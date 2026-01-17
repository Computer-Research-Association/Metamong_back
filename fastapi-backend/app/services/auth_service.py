from sqlalchemy.orm import Session
from typing import Dict, Any


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

        return {}
