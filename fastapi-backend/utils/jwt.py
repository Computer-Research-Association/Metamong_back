from datetime import datetime, timedelta # 날짜 및 시간 계산
from typing import Optional # 값이 있을 수도 없을 수도 있음을 표시
from jose import JWTError, jwt # JWT 생성/검증 라이브러리
from config import settings # config.py 에서 만든 설정 객체


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 토큰 생성 함수
    - data: 토큰에 담을 정보(이메일, 이름 등)
    - expires_delta: 만료 시간(선택, 없으면 기본값 사용)
    str: 반환 타입은 문자열
    """
    to_encode = data.copy() # 입력 데이터 복사(원본 보호)
    
    # expires_delta가 있으면 그 값 사용, 없으면 설정값(기본 24시간) 사용
    if expires_delta: # 만료 시간 설정
        expire = datetime.utcnow() + expires_delta 
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    # 토큰에 만료 시간(exp) 추가
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    JWT 토큰 검증 함수
    -> Optional[dict]: 성공 시 딕셔너리, 실패 시 None
    """
    # 토큰 디코딩 및 검증
    # 서명이 맞고 만료되지 않았으면 payload 반환
    # 오류 시 None 반환
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
