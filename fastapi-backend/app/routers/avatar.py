"""
Avatar API 라우터.

- GET /avatars/{avatar_id}: id로 아바타 조회
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.avatar import AvatarResponse
from app.db.database import get_db
from app.services.avatar_service import AvatarService

router = APIRouter(prefix="/avatars", tags=["avatars"])


@router.get("/{avatar_id}", response_model=AvatarResponse)
async def get_avatar(avatar_id: int, db: Session = Depends(get_db)):
    """
    아바타 id로 아바타 정보를 조회합니다. 없으면 404를 반환합니다.
    """
    avatar_service = AvatarService(db)
    avatar = avatar_service.get_avatar_by_id(avatar_id)
    if avatar is None:
        raise HTTPException(status_code=404, detail="아바타를 찾을 수 없습니다.")
    return avatar
