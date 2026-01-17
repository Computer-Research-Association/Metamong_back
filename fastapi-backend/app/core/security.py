from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from app.core.config import settings


def create_access_token(subject: Any, expires_delta: timedelta | None = None) -> str:
