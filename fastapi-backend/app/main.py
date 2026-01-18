from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.routers import auth

app = FastAPI(title=settings.PROJECT_NAME)

# Authlib 세션 관리
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
# Router 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-backend!", "version": "3.11"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
