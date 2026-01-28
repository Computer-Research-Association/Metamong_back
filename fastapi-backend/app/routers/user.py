from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, RCUpdate, InitializeUserInfo
from app.db.models import User
from app.db.enums import UserStatus
from app.services.user_service import UserService
from app.db.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/rc", response_model=UserResponse)
async def update_my_rc(
    rc_data: RCUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    updated_user = user_service.update_user_rc(current_user, rc_data.rc)
    return updated_user


@router.patch("/me/initialize", response_model=UserResponse)
async def initialize_user_info(
    init_data: InitializeUserInfo,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    updated_user = user_service.initialize_user_info(current_user, init_data)
    return updated_user
