from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-backend!", "version": "3.11"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
