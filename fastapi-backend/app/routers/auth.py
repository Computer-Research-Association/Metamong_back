from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.core.oauth import oauth
from app.core.config import settings
from app.core.security import create_access_token
from app.db.database import get_db
from app.db.models import User
from app.db.enums import AuthProvider, RC, UserStatus
from app.services.auth_service import AuthService
from app.schemas.auth import SymmetricKeyResponse, Token

router = APIRouter()


@router.post("/dev-login", response_model=Token)
def dev_login(db: Session = Depends(get_db)):
    """
    개발 환경 전용 로그인 (NODE_ENV=development 시에만 활성화)
    Unity 에디터에서 WebGL 빌드 없이 테스트용 admin 계정으로 바로 로그인할 때 사용
    """
    if settings.NODE_ENV != "development":
        raise HTTPException(status_code=404, detail="Not found")

    user = db.query(User).filter(
        User.email == "dev@metamong.local",
        User.auth_provider == AuthProvider.LOCAL
    ).first()

    if not user:
        user = User(
            email="dev@metamong.local",
            nickname="DevAdmin",
            real_name="Dev Admin",
            auth_provider=AuthProvider.LOCAL,
            rc=RC.Torrey,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        nickname=user.nickname,
    )


@router.get("/key", response_model=SymmetricKeyResponse)
async def get_symmetric_key():
    """
    토큰 검증용 대칭키를 응답 body로 리턴함
    """
    if not settings.JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT secret not configured")
    return SymmetricKeyResponse(
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider not in ["google", "naver", "kakao"]:
        raise HTTPException(status_code=404, detail="Invalid provider")

    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth client for {provider} is not configured"
        )

    redirect_uri = f"{settings.BACKEND_URL}/api/auth/callback/{provider}"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}")
async def auth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    try:
        client = oauth.create_client(provider)
        if client is None:
            raise HTTPException(
                status_code=500,
                detail=f"OAuth client for {provider} is not configured"
            )

        token = await client.authorize_access_token(request)

        # Service Layer
        auth_service = AuthService(db)
        user_data = await auth_service.get_user_info(provider, client, token)
        access_token = await auth_service.login(provider, user_data)

        redirect_url = f"{settings.FRONTEND_URL}?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed: Unknown")
