"""
팀(Team) 비즈니스 로직 서비스.

DB 세션을 받아 팀 생성 등 팀 관련 작업을 수행
라우터에서는 요청/응답만 다루고, 실제 DB 작업과 검증은 여기서 처리
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import Team, User
from app.schemas.team import TeamCreate


class TeamService:
    def __init__(self, db: Session):
        self.db = db

    def create_team(self, owner: User, create_data: TeamCreate) -> Team:
        """
        팀을 생성합니다. 소유자(owner)는 로그인한 현재 유저로 설정

        :param owner: 팀 소유자 (현재 인증된 유저)
        :param create_data: 팀 이름 등 생성 요청 데이터
        :return: 생성된 Team 엔티티 (owner relationship 로드됨)
        :raises: 이름 중복 시 IntegrityError → 라우터에서 400으로 변환 가능
        """
        team = Team(
            name=create_data.name.strip(),
            owner_user_id=owner.id,
        )
        self.db.add(team)
        try:
            self.db.commit()
            self.db.refresh(team)
            # 응답에서 owner(유저 정보)를 쓰기 위해 relationship 로드
            _ = team.owner
            return team
        except IntegrityError:
            self.db.rollback()
            raise
