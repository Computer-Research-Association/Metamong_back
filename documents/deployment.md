# 배포 및 로컬 테스트 가이드

Docker Compose와 GitHub Actions(appleboy/ssh-action)를 사용한 배포 구성입니다.

---

## 목차

1. [전체 구성 개요](#전체-구성-개요)
2. [서비스 구성](#서비스-구성)
3. [환경변수 관리](#환경변수-관리)
4. [로컬 테스트](#로컬-테스트)
5. [GitHub Actions CI/CD](#github-actions-cicd)
6. [서버 최초 설정](#서버-최초-설정)
7. [수동 배포](#수동-배포)
8. [로그 확인](#로그-확인)
9. [트러블슈팅](#트러블슈팅)

---

## 전체 구성 개요

```
GitHub (main 브랜치 push 또는 수동 실행)
    ↓
GitHub Actions (ubuntu-latest)
    ↓  SSH (appleboy/ssh-action)
홈서버 (Ubuntu 24.04)
    ↓
git pull → .env 재생성 → docker compose down → docker compose up --build -d
    ↓
[db: PostgreSQL] ← [fastapi: FastAPI :8000] ← [colyseus: Colyseus :2567]
```

Self-hosted Runner 없이 GitHub Actions 무료 플랜에서 동작합니다.

---

## 서비스 구성

`docker-compose.yml` 기준:

| 서비스 | 빌드 | 포트 | 의존성 |
|--------|------|------|--------|
| `db` | `postgres:15-alpine` | 5432 | - |
| `fastapi` | `./fastapi-backend` | 8000 | db |
| `colyseus` | `./colyseus-server` | 2567 | fastapi |

### 내부 네트워크

세 서비스는 `metaverse-network` (bridge)로 연결됩니다.

- Colyseus → FastAPI: `http://fastapi:8000`
- FastAPI → DB: `postgresql://team_admin:<DB_PASSWORD>@db:5432/metaverse_db`

### 데이터 영구 보존

PostgreSQL 데이터는 `./postgres_data` 볼륨에 저장됩니다. 컨테이너를 재시작해도 데이터는 유지됩니다.

---

## 환경변수 관리

### 환경변수 목록

| 변수명 | 용도 | 로컬 | 배포(GitHub Secrets) |
|--------|------|------|----------------------|
| `DB_PASSWORD` | PostgreSQL 비밀번호 | ✅ | ✅ |
| `JWT_SECRET` | JWT 서명 대칭키 | ✅ | ✅ |
| `SECRET_KEY` | Starlette 세션 시크릿 | ✅ | ✅ |
| `GOOGLE_CLIENT_ID` | Google OAuth 클라이언트 ID | ✅ | ✅ |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 클라이언트 Secret | ✅ | ✅ |
| `BACKEND_URL` | FastAPI 공개 URL (OAuth 콜백) | ✅ | ✅ |
| `FRONTEND_URL` | Unity WebGL 호스팅 URL | ✅ | ✅ |
| `SSH_HOST` | 홈서버 도메인/IP | - | ✅ |
| `SSH_PORT` | SSH 포트 | - | ✅ |
| `SSH_USER` | SSH 접속 유저명 | - | ✅ |
| `SSH_PRIVATE_KEY` | SSH 개인 키 (PEM 전체) | - | ✅ |

### 환경변수 흐름

**로컬**: 루트 `.env` → `docker-compose.yml`이 읽어 각 컨테이너 `environment:`로 주입

**배포**: GitHub Secrets → Actions에서 SSH로 서버에 전달 → 서버 루트 `.env` 재생성 → `docker-compose.yml`이 읽어 주입

> FastAPI 컨테이너는 `environment:` 블록을 통해 env var를 받으며, 컨테이너 내부 `.env` 파일에 의존하지 않습니다.

---

## 로컬 테스트

### 1. 사전 요구사항

- Docker Desktop (또는 Docker Engine + docker-compose-plugin)
- Git

### 2. 레포 클론

```bash
git clone https://github.com/Computer-Research-Association/Metamong_back.git
cd Metamong_back
```

### 3. `.env` 파일 생성

루트의 `.env.example`을 복사해 `.env`를 만들고 값을 채웁니다.

```bash
cp .env.example .env
```

```env
# .env (루트)
DB_PASSWORD=local_db_password
JWT_SECRET=local_jwt_secret
SECRET_KEY=local_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
NODE_ENV=development
```

> Google OAuth 테스트가 불필요하면 `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`은 임의 문자열로 채워도 서버 기동에는 문제 없습니다.

### 4. 서비스 실행

```bash
docker compose up --build -d
```

### 5. DB 마이그레이션 (최초 1회 또는 모델 변경 시)

```bash
docker exec fastapi-app uv run alembic upgrade head
```

### 6. 동작 확인

| 서비스 | 확인 방법 |
|--------|-----------|
| FastAPI | `http://localhost:8000/docs` (Swagger UI) |
| Colyseus | `http://localhost:2567` |
| PostgreSQL | `localhost:5432` (DB 클라이언트로 접속) |

### 7. 서비스 종료

```bash
docker compose down
```

데이터까지 초기화하려면:

```bash
docker compose down -v
sudo rm -rf ./postgres_data
```

---

## GitHub Actions CI/CD

`.github/workflows/deploy.yml`

### 트리거 조건

- `main` 브랜치에 push 시 자동 실행
- GitHub Actions 탭에서 수동 실행 가능 (`workflow_dispatch`)

### 파이프라인 단계

```
1. SSH로 홈서버 접속 (appleboy/ssh-action)
2. git pull origin main          — 최신 코드 반영
3. .env 재생성                   — GitHub Secrets에서 값을 받아 덮어씀
4. docker compose down           — 기존 컨테이너 종료
5. docker compose up --build -d  — 새 이미지 빌드 및 재기동
6. docker image prune -f         — 미사용 구 이미지 삭제
```

### GitHub Secrets 등록 방법

리포지토리 → Settings → Secrets and variables → Actions → New repository secret

등록해야 할 항목: 위 [환경변수 목록](#환경변수-목록)의 "배포(GitHub Secrets)" 열 참고

### 새 환경변수 추가 시

1. GitHub Secrets에 새 Secret 추가
2. `deploy.yml`의 `envs:`, `script` 내 `cat > .env`, `env:` 블록 세 곳에 추가
3. `docker-compose.yml` fastapi `environment:`에 추가

---

## 서버 최초 설정

서버를 새로 세팅하거나 포맷 후 1회 수행합니다.

### 1. Docker 설치

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker  # 재로그인 없이 즉시 적용
```

### 2. SSH 공개 키 등록 (GitHub Actions 접속용)

로컬 머신에서 키 쌍 생성:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
```

공개 키(`id_ed25519.pub`)를 서버의 `~/.ssh/authorized_keys`에 추가하고,
개인 키(`id_ed25519`) 전체 내용을 GitHub Secrets의 `SSH_PRIVATE_KEY`에 등록합니다.

### 3. 레포 클론

```bash
git clone https://github.com/Computer-Research-Association/Metamong_back.git /home/metamong/Metamong_back
```

### 4. 최초 배포

GitHub Actions를 수동 실행하거나(`workflow_dispatch`), `main` 브랜치에 push하면 자동 배포됩니다.

수동으로 직접 실행하려면 [수동 배포](#수동-배포) 항목을 참고하세요.

### 5. 최초 DB 마이그레이션

```bash
cd /home/metamong/Metamong_back
docker exec fastapi-app uv run alembic upgrade head
```

---

## 수동 배포

서버에 SSH 접속 후:

```bash
cd /home/metamong/Metamong_back

git pull origin main

# 환경변수 변경이 있으면 .env도 수동으로 수정
nano .env

docker compose down
docker compose up --build -d

# 로그로 정상 기동 확인
docker compose logs -f
```

---

## 로그 확인

```bash
# 전체 서비스 실시간 로그
docker compose logs -f

# 특정 서비스
docker compose logs -f fastapi
docker compose logs -f colyseus
docker compose logs -f db

# 최근 100줄만
docker compose logs --tail=100 fastapi
```

---

## 트러블슈팅

### 서비스가 시작되지 않을 때

```bash
docker compose ps          # 컨테이너 상태 확인
docker compose logs fastapi  # 오류 메시지 확인
```

### 환경변수 누락 오류

컨테이너 내부에서 env var 확인:

```bash
docker exec fastapi-app env | grep JWT_SECRET
```

루트 `.env` 파일이 존재하고 올바른 값이 들어 있는지 확인합니다.

### DB 연결 오류

FastAPI가 DB보다 먼저 시작되면 연결에 실패할 수 있습니다.

```bash
docker compose restart fastapi
```

### 포트 충돌

```bash
sudo lsof -i :8000
sudo lsof -i :2567
sudo lsof -i :5432
```

### 이미지 빌드 실패

```bash
# 캐시 없이 재빌드
docker compose build --no-cache

# 사용하지 않는 이미지/컨테이너 전체 정리 (주의: 모든 이미지 삭제)
docker system prune -a
```

### DB 마이그레이션 필요

모델 변경 후 배포 시:

```bash
docker exec fastapi-app uv run alembic upgrade head
```

### postgres_data 권한 오류

```bash
sudo chown -R 999:999 ./postgres_data
```
