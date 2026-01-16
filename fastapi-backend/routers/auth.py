from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from google.auth.transport import requests
from google.oauth2 import id_token
import httpx
from config import settings
from utils.jwt import create_access_token, verify_token

# FastAPI 라우터 생성 (prefix는 모든 경로 앞에 붙음)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def google_login():
    """
    Google OAuth 로그인 URL 생성
    사용자가 이 엔드포인트를 호출하면 Google 로그인 페이지로 이동할 수 있는 URL을 반환
    """
    # Client ID가 설정되지 않았으면 에러
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID가 설정되지 않았습니다.")
    
    # Google OAuth 인증 URL 생성
    # 이 URL로 사용자를 리디렉션하면 Google 로그인 페이지가 나타남
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"  # 우리 앱의 Client ID
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"  # 로그인 후 돌아올 주소
        f"response_type=code&"  # Authorization Code 방식 사용
        f"scope=openid email profile&"  # 요청하는 권한 (이메일, 프로필 정보)
        f"access_type=offline&"  # Refresh Token도 받기 위해
        f"prompt=consent"  # 사용자에게 동의 화면 보여주기
    )
    
    # JSON 형태로 URL 반환 (프론트엔드에서 이 URL로 리디렉션)
    return {"auth_url": google_auth_url}


@router.get("/google/callback")
async def google_callback(code: str):
    """
    Google OAuth 콜백 처리
    Google이 로그인 후 이 엔드포인트로 사용자를 리디렉션함
    code 파라미터에 Authorization Code가 포함되어 있음
    """
    # Authorization Code가 없으면 에러
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code가 없습니다.")
    
    try:
        # 1단계: Authorization Code를 Access Token으로 교환
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,  # Google에서 받은 Authorization Code
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",  # OAuth 2.0 표준 방식
        }
        
        # HTTP POST 요청으로 토큰 교환
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()  # 에러가 있으면 예외 발생
            tokens = token_response.json()  # 응답을 JSON으로 파싱
        
        # ID Token 추출 (사용자 정보가 들어있음)
        id_token_str = tokens.get("id_token")
        if not id_token_str:
            raise HTTPException(status_code=400, detail="ID token을 받지 못했습니다.")
        
        # 2단계: ID Token 검증 및 사용자 정보 추출
        try:
            # Google의 공개키로 ID Token 검증 (위조 방지)
            user_info = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            raise HTTPException(status_code=401, detail="유효하지 않은 ID token입니다.")
        
        # 3단계: 사용자 정보 추출
        email = user_info.get("email")  # 이메일
        name = user_info.get("name")  # 이름
        picture = user_info.get("picture")  # 프로필 사진 URL
        google_id = user_info.get("sub")  # Google 고유 ID
        
        if not email:
            raise HTTPException(status_code=400, detail="이메일 정보를 가져올 수 없습니다.")
        
        # 4단계: JWT 토큰 생성 (우리 앱의 인증 토큰)
        jwt_data = {
            "sub": email,  # subject (주체) - 보통 사용자 식별자
            "email": email,
            "name": name,
            "picture": picture,
            "google_id": google_id,
        }
        # JWT 토큰 생성 (24시간 유효)
        access_token = create_access_token(data=jwt_data)
        
        # 5단계: 프론트엔드로 리디렉션 (토큰 포함)
        # 실제로는 프론트엔드 URL로 리디렉트하고 토큰을 쿼리 파라미터로 전달
        # 프론트엔드에서 이 토큰을 저장하고 이후 API 요청 시 사용
        frontend_url = f"http://localhost:3000/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except httpx.HTTPStatusError as e:
        # HTTP 요청 에러 처리
        raise HTTPException(status_code=400, detail=f"토큰 교환 실패: {e.response.text}")
    except Exception as e:
        # 기타 예상치 못한 에러 처리
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류 발생: {str(e)}")


@router.get("/me")
async def get_current_user(token: str):
    """
    현재 로그인한 사용자 정보 조회
    프론트엔드에서 JWT 토큰을 보내면 사용자 정보를 반환
    """
    # JWT 토큰 검증
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
    # 토큰에서 사용자 정보 추출하여 반환
    return {
        "email": payload.get("email"),
        "name": payload.get("name"),
        "picture": payload.get("picture"),
        "google_id": payload.get("google_id"),
    }
