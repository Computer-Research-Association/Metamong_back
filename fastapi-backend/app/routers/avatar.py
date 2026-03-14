"""
Avatar API 라우터.

- POST /avatars/create: 새 아바타 생성 (인증 필요, 현재 유저 소유로 생성)
- GET /avatars/list: 본인 아바타 목록 조회 (인증 필요, 본인만)
- GET /avatars/{avatar_id}: id로 아바타 조회
- DELETE /avatars/{avatar_id}: id로 아바타 삭제 (소유자만 가능)
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.avatar import AvatarCreate, AvatarResponse
from app.db.models import User
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.services.avatar_service import AvatarService

router = APIRouter(prefix="/avatars", tags=["avatars"])


@router.post("/create", response_model=AvatarResponse, status_code=201)
async def create_avatar(
    create_data: AvatarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    새 아바타를 생성합니다. 로그인한 유저가 소유자가 되며, avatar_asset_id와 nickname을 body로 전달합니다.
    """
    avatar_service = AvatarService(db)
    avatar = avatar_service.create_avatar(current_user, create_data)
    return avatar


@router.get("/list", response_model=List[AvatarResponse])
async def list_avatars_by_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    로그인한 유저(본인)의 모든 아바타를 조회합니다. 본인 외에는 조회할 수 없습니다. 빈 목록이면 []를 반환합니다.
    """
    avatar_service = AvatarService(db)
    avatars = avatar_service.get_avatars_by_user_id(current_user.id)
    return avatars


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


@router.delete("/{avatar_id}", status_code=204)
async def delete_avatar(
    avatar_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    아바타 id로 아바타를 삭제합니다. 본인 소유 아바타만 삭제 가능하며, 없으면 404, 권한 없으면 403을 반환합니다.
    """
    avatar_service = AvatarService(db)
    avatar = avatar_service.get_avatar_by_id(avatar_id)
    if avatar is None:
        raise HTTPException(status_code=404, detail="아바타를 찾을 수 없습니다.")
    if avatar.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인의 아바타만 삭제할 수 있습니다.")
    avatar_service.delete_avatar(avatar)
