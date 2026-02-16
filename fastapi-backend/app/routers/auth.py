from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse

from app.core.oauth import oauth
from app.core.config import settings
from app.db.database import get_db
from app.services.auth_service import AuthService

router = APIRouter()


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

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Success</title>
        </head>
        <body>
            <h2>로그인 성공!</h2>
            <p>잠시 후 게임으로 돌아갑니다...</p>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_success',
                        token: '{access_token}'
                    }}, '{settings.FRONTEND_URL}');
                    window.close();
                }} else {{
                    window.location.href = '{settings.FRONTEND_URL}/auth/callback?token={access_token}';
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except ValueError as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <body>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_error',
                        error: '{str(e)}'
                    }}, '{settings.FRONTEND_URL}');
                    window.close();
                }}
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <body>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_error',
                        error: 'Login failed'
                    }}, '{settings.FRONTEND_URL}');
                    window.close();
                }}
            </script>
        </body>
        </html>
        """)
