from fastapi import FastAPI

from app.db.database import engine
from app.db import models

from app.core.config import settings

# TODO: 서버 본격 배포 시 Alembic 도입 필요
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-backend!", "version": "3.11"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
