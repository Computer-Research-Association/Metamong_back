from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserUpdate, InitializeUserInfo
from app.db.models import User
from app.services.user_service import UserService
from app.db.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not update_data.model_fields_set:
        raise HTTPException(status_code=400, detail="No fields to update")

    user_service = UserService(db)
    updated_user = user_service.update_user(current_user, update_data)
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
