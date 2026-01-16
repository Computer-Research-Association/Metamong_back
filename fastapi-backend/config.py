import os # 환경 변수 읽기 위해 사용
from dotenv import load_dotenv # .env 파일을 읽어 환경 변수로 로드

load_dotenv() # .env 파일을 읽어 환경 변수로 로드

class Settings: # 설정값 모아두는 클래스
    # Google OAuth 설정
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    # JWT 설정
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production") #JWT 서명용 비밀키
    JWT_ALGORITHM: str = "HS256" #JWT 서명 알고리즘
    JWT_EXPIRATION_HOURS: int = 24 # 토큰 만료 시간(시간 단위)
    
    # 서버 설정
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")


settings = Settings()
