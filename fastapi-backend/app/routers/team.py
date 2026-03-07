"""
팀(Team) API 라우터.

팀에 대한 REST API 엔드포인트를 정의합니다.
- POST /teams/create: 팀 생성 (현재 로그인 유저를 소유자로 팀 추가)
- GET /teams/{team_id}: id로 팀 조회 (인증 불필요)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.team import TeamCreate, TeamResponse
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
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="이미 같은 이름의 팀이 존재합니다.",
        )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    팀 id로 팀 정보를 조회합니다. 팀이 없으면 404를 반환합니다.
    """
    team_service = TeamService(db)
    team = team_service.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다.")
    return team
