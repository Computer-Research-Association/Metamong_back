from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db.enums import AuthProvider, RC, UserStatus


class UserResponse(BaseModel):
    id: int
    email: Optional[EmailStr]
    nickname: str
    real_name: str
    auth_provider: AuthProvider
    rc: RC
    status: UserStatus

    class Config:
        from_attributes = True

