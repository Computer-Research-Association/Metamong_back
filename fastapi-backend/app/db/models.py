from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
