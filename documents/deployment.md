# 배포 가이드

Docker Compose와 GitHub Actions를 사용한 자동 배포 구성입니다.

---

## 목차

1. [전체 구성 개요](#전체-구성-개요)
2. [서비스 구성](#서비스-구성)
3. [GitHub Actions CI/CD](#github-actions-cicd)
4. [최초 서버 설정](#최초-서버-설정)
5. [수동 배포 방법](#수동-배포-방법)
6. [환경변수 관리](#환경변수-관리)
7. [로그 확인](#로그-확인)
8. [트러블슈팅](#트러블슈팅)

---

## 전체 구성 개요

```
GitHub (main 브랜치 push)
    ↓
GitHub Actions
    ↓
Self-hosted Runner (미니 PC)
    ↓
docker compose down → docker compose up --build -d
    ↓
[db: PostgreSQL] ← [fastapi: FastAPI] ← [colyseus: Colyseus]
```

배포는 `main` 브랜치에 push 될 때 또는 GitHub Actions에서 수동 실행 시 자동으로 진행됩니다.

---

## 서비스 구성

`docker-compose.yml` 기준:

| 서비스 | 이미지/빌드 | 포트 | 의존성 |
|--------|------------|------|--------|
| `db` | `postgres:15-alpine` | 5432 | - |
| `fastapi` | `./fastapi-backend` 빌드 | 8000 | db |
| `colyseus` | `./colyseus-server` 빌드 | 2567 | fastapi |

### 내부 네트워크

세 서비스는 `metaverse-network` (bridge 드라이버)로 연결됩니다.
- Colyseus → FastAPI: `http://fastapi:8000` (컨테이너 이름으로 통신)
- FastAPI → DB: `postgresql://team_admin:<password>@db:5432/metaverse_db`

### 데이터 영구 보존

PostgreSQL 데이터는 `./postgres_data` 볼륨에 저장됩니다.
서버를 재시작해도 데이터가 유지됩니다.

---

## GitHub Actions CI/CD

`.github/workflows/deploy.yml`

### 트리거 조건
- `main` 브랜치에 push 시 자동 실행
- GitHub Actions 탭에서 수동 실행 가능 (`workflow_dispatch`)

### 파이프라인 단계

```
1. Checkout code          - 최신 코드 가져오기
2. Create .env file       - GitHub Secrets에서 환경변수 주입
3. Docker Compose Deploy  - docker compose down → up --build -d
4. Cleanup Docker images  - 사용하지 않는 구 이미지 삭제
```

### GitHub Secrets 설정 필요 항목

GitHub 리포지토리 → Settings → Secrets and variables → Actions에서 설정:

| Secret 이름 | 설명 |
|-------------|------|
| `DB_PASSWORD` | PostgreSQL 비밀번호 |
| `JWT_SECRET` | JWT 서명 대칭키 |

> `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` 등 추가 환경변수가 필요하면
> `deploy.yml`의 "Create .env file" 단계에 추가하고, GitHub Secrets에도 등록해야 합니다.

---

## 최초 서버 설정

Self-hosted Runner가 설치된 서버(미니 PC)에서 최초 1회 설정합니다.

### 1. Docker 설치

```bash
# Ubuntu 기준
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. GitHub Actions Self-hosted Runner 설치

GitHub 리포지토리 → Settings → Actions → Runners → New self-hosted runner
페이지의 안내에 따라 설치합니다.

### 3. 리포지토리 클론

```bash
git clone https://github.com/Computer-Research-Association/Metamong_back.git
cd Metamong_back
```

### 4. 최초 배포

```bash
# .env 파일 생성 (GitHub Secrets 없이 수동 실행 시)
echo "DB_PASSWORD=your_password" > .env
echo "JWT_SECRET=your_jwt_secret" >> .env

# 서비스 시작
docker compose up --build -d
```

### 5. DB 마이그레이션 최초 적용

컨테이너가 실행 중인 상태에서:

```bash
docker exec fastapi-app uv run alembic upgrade head
```

---

## 수동 배포 방법

서버에 SSH로 접속 후:

```bash
cd /path/to/Metamong_back

# 최신 코드 가져오기
git pull origin main

# 재빌드 및 재시작
docker compose down
docker compose up --build -d

# 로그 확인
docker compose logs -f
```

---

## 환경변수 관리

### 로컬 `.env` 파일 구조

```env
# DB
DB_PASSWORD=your_db_password

# JWT
JWT_SECRET=your_jwt_secret_key_here
NODE_ENV=production

# FastAPI 추가 환경변수 (docker-compose.yml에 추가 필요)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
BACKEND_URL=https://your-server-domain.com
FRONTEND_URL=https://your-unity-webgl-host.com
SECRET_KEY=your_session_secret_key
```

> `.env` 파일은 `.gitignore`에 포함되어 있어 절대 커밋되지 않습니다.

### 추가 환경변수를 배포에 포함하는 방법

1. GitHub Secrets에 새 Secret 추가 (예: `GOOGLE_CLIENT_ID`)
2. `deploy.yml`의 "Create .env file" 단계에 추가:
```yaml
- name: Create .env file
  run: |
    echo "DB_PASSWORD=${{ secrets.DB_PASSWORD }}" >> .env
    echo "JWT_SECRET=${{ secrets.JWT_SECRET }}" >> .env
    echo "GOOGLE_CLIENT_ID=${{ secrets.GOOGLE_CLIENT_ID }}" >> .env  # 추가
```

---

## 로그 확인

```bash
# 전체 서비스 로그 (실시간)
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f fastapi
docker compose logs -f colyseus
docker compose logs -f db

# 마지막 100줄만
docker compose logs --tail=100 fastapi
```

---

## 트러블슈팅

### 서비스가 시작되지 않을 때

```bash
# 컨테이너 상태 확인
docker compose ps

# 특정 서비스 로그로 오류 확인
docker compose logs fastapi
```

### DB 연결 오류

FastAPI가 DB보다 먼저 시작되면 연결 실패할 수 있습니다.

```bash
# DB가 완전히 시작될 때까지 대기 후 FastAPI만 재시작
docker compose restart fastapi
```

### 포트 충돌

```bash
# 포트 사용 프로세스 확인
sudo lsof -i :8000
sudo lsof -i :2567
sudo lsof -i :5432
```

### 이미지 빌드 실패

```bash
# 캐시 없이 재빌드
docker compose build --no-cache

# 사용하지 않는 이미지/컨테이너 모두 정리
docker system prune -a
```

### DB 마이그레이션 필요

모델 변경 후 배포 시 컨테이너 내부에서 마이그레이션을 실행해야 합니다:

```bash
docker exec fastapi-app uv run alembic upgrade head
```

### postgres_data 권한 오류

```bash
sudo chown -R 999:999 ./postgres_data
```
