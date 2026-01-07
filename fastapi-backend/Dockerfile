FROM astral-sh/uv:python3.11-bookworm-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치 (캐시 활용을 위해 소스 코드보다 먼저 복사)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-cache

# 소스 코드 복사
COPY . .

# 실행 (uv run을 통해 설치된 환경에서 실행)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]