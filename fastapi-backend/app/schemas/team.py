"""
팀(Team) API 요청/응답 스키마.

- TeamCreate: 팀 생성 시 클라이언트가 보내는 body (이름만 필요, 소유자는 로그인 유저로 설정됨)
- TeamResponse: 팀 생성·조회 시 API가 반환하는 형태 (id, name, owner_user_id, created_at, owner 유저 정보)
"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class TeamCreate(BaseModel):
    """팀 생성 요청 body. 팀 이름만 받고, 소유자(owner)는 인증된 현재 유저로 설정됨."""

    name: str = Field(..., min_length=1, max_length=50, description="팀 이름")


class TeamResponse(BaseModel):
    """팀 API 응답 스키마. DB Team 모델과 동일한 필드 + 소유자(owner) 유저 정보."""

    id: int
    name: str
    owner_user_id: int
    created_at: datetime
    owner: UserResponse | None = None  # 팀을 만든 유저 정보 (relationship)

    class Config:
        from_attributes = True
