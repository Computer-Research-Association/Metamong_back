from fastapi import APIRouter, Request, HTTPException

from app.core.oauth import oauth
from app.core.config import settings

router = APIRouter()


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider not in ["google", "naver", "kakao"]:
        raise HTTPException(status_code=404, detail="Invalid provider")

    client = oauth.create_client(provider)
    redirect_uri = f"{settings.BACKEND_URL}/api/auth/callback/{provider}"
    return await client.authorize_redirect(request, redirect_uri)
