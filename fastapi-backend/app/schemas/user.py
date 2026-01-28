from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db.enums import AuthProvider, RC, UserStatus, MBTI


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


class RCUpdate(BaseModel):
    rc: RC


class InitializeUserInfo(BaseModel):
    student_id: Optional[str] = None
    major: Optional[str] = None
    phone_number: Optional[str] = None
    instagram_id: Optional[str] = None
    mbti: Optional[MBTI] = None
