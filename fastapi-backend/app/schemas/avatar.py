"""
Avatar API 응답 스키마.
"""
from pydantic import BaseModel


class AvatarResponse(BaseModel):
    """Avatar 조회 시 API가 반환하는 형태."""

    id: int
    user_id: int
    avatar_asset_id: str
    nickname: str

    class Config:
        from_attributes = True
