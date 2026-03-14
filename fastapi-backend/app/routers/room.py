from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.schemas.room_role import RoomRoleListResponse, RoomRoleResponse, RoomRoleUpdateRequest
from app.schemas.room_layout import (
    PatchObjectsRequest,
    PatchObjectsResponse,
    PatchPortalsRequest,
    PatchPortalsResponse,
    PatchTilesRequest,
    PatchTilesResponse,
    ReplaceObjectsRequest,
    ReplaceObjectsResponse,
    ReplacePortalsRequest,
    ReplacePortalsResponse,
    ReplaceTilesRequest,
    ReplaceTilesResponse,
    RoomLayoutResponse,
)
from app.schemas.room import RoomCreate, RoomListResponse, RoomResponse, RoomUpdate
from app.services.room_layout_service import RoomLayoutService
from app.services.room_role_service import RoomRoleService
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=RoomListResponse)
# 룸 목록 조회 API
async def list_rooms(
    mine_only: bool = False,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be 0 or greater")

    room_service = RoomService(db)
    total, rooms = room_service.list_rooms(
        user=current_user,
        limit=limit,
        offset=offset,
        mine_only=mine_only,
    )
    return RoomListResponse(total=total, limit=limit, offset=offset, rooms=rooms)


@router.post("", response_model=RoomResponse)
# 룸 생성 API
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_service = RoomService(db)
    room = room_service.create_room(current_user, room_data)
    return room


@router.get("/{room_id}", response_model=RoomResponse)
# 룸 상세 조회 API
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_service = RoomService(db)
    room = room_service.get_room(room_id, current_user)
    return room


@router.patch("/{room_id}", response_model=RoomResponse)
# 룸 수정 API
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not room_data.model_fields_set:
        raise HTTPException(status_code=400, detail="No fields to update")

    room_service = RoomService(db)
    room = room_service.update_room(room_id, current_user, room_data)
    return room


@router.get("/{room_id}/layout", response_model=RoomLayoutResponse)
# 룸 레이아웃 조회 API
async def get_room_layout(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    return room_layout_service.get_layout(room_id, current_user)


@router.put("/{room_id}/tiles", response_model=ReplaceTilesResponse)
# 룸 타일 일괄 교체 API
async def replace_room_tiles(
    room_id: int,
    request_data: ReplaceTilesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    tiles = room_layout_service.replace_tiles(room_id, current_user, request_data)
    return ReplaceTilesResponse(room_id=room_id, tiles=tiles)


@router.patch("/{room_id}/tiles", response_model=PatchTilesResponse)
# 룸 타일 부분 수정 API
async def patch_room_tiles(
    room_id: int,
    request_data: PatchTilesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    tiles = room_layout_service.patch_tiles(room_id, current_user, request_data)
    return PatchTilesResponse(room_id=room_id, tiles=tiles)


@router.put("/{room_id}/objects", response_model=ReplaceObjectsResponse)
# 룸 오브젝트 일괄 교체 API
async def replace_room_objects(
    room_id: int,
    request_data: ReplaceObjectsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    objects = room_layout_service.replace_objects(room_id, current_user, request_data)
    return ReplaceObjectsResponse(room_id=room_id, objects=objects)


@router.patch("/{room_id}/objects", response_model=PatchObjectsResponse)
# 룸 오브젝트 부분 수정 API
async def patch_room_objects(
    room_id: int,
    request_data: PatchObjectsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    objects = room_layout_service.patch_objects(room_id, current_user, request_data)
    return PatchObjectsResponse(room_id=room_id, objects=objects)


@router.put("/{room_id}/portals", response_model=ReplacePortalsResponse)
# 룸 포탈 일괄 교체 API
async def replace_room_portals(
    room_id: int,
    request_data: ReplacePortalsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    portals = room_layout_service.replace_portals(room_id, current_user, request_data)
    return ReplacePortalsResponse(room_id=room_id, portals=portals)


@router.patch("/{room_id}/portals", response_model=PatchPortalsResponse)
# 룸 포탈 부분 수정 API
async def patch_room_portals(
    room_id: int,
    request_data: PatchPortalsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_layout_service = RoomLayoutService(db)
    portals = room_layout_service.patch_portals(room_id, current_user, request_data)
    return PatchPortalsResponse(room_id=room_id, portals=portals)


@router.get("/{room_id}/roles", response_model=RoomRoleListResponse)
# 룸 역할 목록 조회 API
async def list_room_roles(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_role_service = RoomRoleService(db)
    roles = room_role_service.list_roles(room_id, current_user)
    return RoomRoleListResponse(room_id=room_id, roles=roles)


@router.get("/{room_id}/roles/me", response_model=RoomRoleResponse)
# 내 역할 조회 API
async def get_my_room_role(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_role_service = RoomRoleService(db)
    return room_role_service.get_role(room_id, current_user.id, current_user)


@router.patch("/{room_id}/roles/{target_user_id}", response_model=RoomRoleResponse)
# 룸 역할 수정 API
async def upsert_room_role(
    room_id: int,
    target_user_id: int,
    request_data: RoomRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_role_service = RoomRoleService(db)
    return room_role_service.upsert_role(
        room_id=room_id,
        target_user_id=target_user_id,
        role=request_data.role,
        current_user=current_user,
    )


@router.get("/{room_id}/roles/{target_user_id}", response_model=RoomRoleResponse)
# 룸 특정 유저 역할 조회 API
async def get_room_role(
    room_id: int,
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room_role_service = RoomRoleService(db)
    return room_role_service.get_role(room_id, target_user_id, current_user)
