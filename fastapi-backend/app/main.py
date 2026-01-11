from fastapi import FastAPI, Depends

from app.db.database import engine, get_db
from app.db import models
from sqlalchemy.orm import Session

from app.core.config import settings

# TODO: 서버 본격 배포 시 Alembic 도입 필요
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-backend!", "version": "3.11"}


@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    return {"message": "DB connection successful"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
