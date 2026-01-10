from fastapi import FastAPI

from app.db.database import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from fastapi-backend!", "version": "3.11"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
