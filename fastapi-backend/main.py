from fastapi import FastAPI
from routers import auth  # routers/auth.py에서 auth 라우터 import

# FastAPI 앱 생성
app = FastAPI(title="FastAPI Backend", version="0.1.0")

# auth 라우터를 앱에 등록
# 이제 /auth/google, /auth/google/callback, /auth/me 엔드포인트가 활성화됨
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-backend!", "version": "3.11"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
