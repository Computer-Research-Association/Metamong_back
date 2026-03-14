"""
Avatar API 요청/응답 스키마.
"""
from pydantic import BaseModel, Field


class AvatarCreate(BaseModel):
    """Avatar 생성 요청 body. user_id는 로그인한 유저로 자동 설정."""

    avatar_asset_id: str = Field(..., min_length=1, max_length=100, description="아바타 에셋 ID")
    nickname: str = Field(..., min_length=1, max_length=50, description="아바타 닉네임")


class AvatarResponse(BaseModel):
    """Avatar 조회 시 API가 반환하는 형태."""

    id: int
    user_id: int
    avatar_asset_id: str
    nickname: str

    class Config:
        from_attributes = True
