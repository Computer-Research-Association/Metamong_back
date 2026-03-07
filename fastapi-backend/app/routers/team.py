"""
팀(Team) API 라우터.

팀에 대한 REST API 엔드포인트를 정의한다.
- POST /teams/create: 팀 생성 (현재 로그인 유저를 소유자로 팀 추가)
- GET /teams: 팀 목록 조회 (최신 생성순, 인증 불필요)
- GET /teams/{team_id}: id로 팀 조회 (인증 불필요)
- PATCH /teams/{team_id}: 팀 이름 수정 (소유자만 가능)
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate
from app.db.models import User
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/create", response_model=TeamResponse)
async def create_team(
    create_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    팀을 생성합니다. 인증된 유저가 소유자(owner)가 되며, 팀 이름만 body로 전달합니다.
    팀 이름이 이미 존재하면 400을 반환합니다.
    """
    team_service = TeamService(db)
    try:
        team = team_service.create_team(current_user, create_data)
        return team
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="이미 같은 이름의 팀이 존재합니다.",
        )


@router.get("/list", response_model=List[TeamResponse])
async def list_teams(db: Session = Depends(get_db)):
    """
    팀 목록을 조회합니다. 최신 생성순으로 반환하며, 각 팀에 소유자(owner) 정보가 포함.
    """
    team_service = TeamService(db)
    teams = team_service.get_teams()
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    팀 id로 팀 정보를 조회한다. 팀이 없으면 404를 반환한다.
    """
    team_service = TeamService(db)
    team = team_service.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다.")
    return team


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    update_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    팀 이름을 수정한다. 팀 소유자만 수정 가능하며, 이름 중복 시 400을 반환함.
    """
    if not update_data.model_fields_set:
        raise HTTPException(status_code=400, detail="수정할 필드가 없습니다.")
    team_service = TeamService(db)
    team = team_service.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다.")
    if team.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="팀 수정 권한이 없습니다.")
    try:
        updated = team_service.update_team(team, update_data)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="이미 같은 이름의 팀이 존재합니다.",
        )
