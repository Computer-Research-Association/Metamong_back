# FastAPI 백엔드 서버 가이드

REST API 서버로, 사용자 인증(OAuth)과 DB 관리를 담당합니다.

---

## 목차

1. [기술 스택](#기술-스택)
2. [디렉토리 구조](#디렉토리-구조)
3. [레이어 구조](#레이어-구조)
4. [API 엔드포인트](#api-엔드포인트)
5. [인증 흐름](#인증-흐름)
6. [데이터베이스 모델](#데이터베이스-모델)
7. [Enum 정의](#enum-정의)
8. [환경변수](#환경변수)
9. [로컬 실행 방법](#로컬-실행-방법)
10. [DB 마이그레이션](#db-마이그레이션)
11. [새 기능 추가 방법](#새-기능-추가-방법)

---

## 기술 스택

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| Python | 3.11 | 런타임 |
| FastAPI | >=0.128 | 웹 프레임워크 |
| SQLAlchemy | >=2.0 | ORM (DB 연동) |
| Alembic | >=1.16 | DB 마이그레이션 |
| Authlib | >=1.6 | OAuth 2.0 클라이언트 |
| python-jose | >=3.5 | JWT 생성/검증 |
| pydantic-settings | >=2.11 | 환경변수 관리 |
| uvicorn | >=0.39 | ASGI 서버 |
| uv | - | 패키지 매니저 |

---

## 디렉토리 구조

```
fastapi-backend/
├── app/
│   ├── main.py              # FastAPI 앱 초기화, 미들웨어, 라우터 등록
│   ├── core/
│   │   ├── config.py        # 환경변수 설정 (Settings 클래스)
│   │   ├── security.py      # JWT 생성/검증 함수
│   │   └── oauth.py         # OAuth 클라이언트 설정 (Google 등)
│   ├── db/
│   │   ├── database.py      # DB 엔진, 세션, Base 정의
│   │   ├── models.py        # SQLAlchemy ORM 모델
│   │   └── enums.py         # DB에서 사용하는 Enum 정의
│   ├── routers/
│   │   ├── auth.py          # /api/auth/* 엔드포인트
│   │   └── user.py          # /api/users/* 엔드포인트
│   ├── services/
│   │   ├── auth_service.py  # 인증 비즈니스 로직
│   │   └── user_service.py  # 유저 비즈니스 로직
│   ├── schemas/
│   │   ├── auth.py          # 인증 관련 Pydantic 스키마
│   │   └── user.py          # 유저 관련 Pydantic 스키마
│   └── dependencies/
│       └── auth.py          # get_current_user 의존성 함수
├── migrations/              # Alembic 마이그레이션 파일
│   └── versions/            # 마이그레이션 이력
├── pyproject.toml           # 프로젝트 의존성 정의
├── alembic.ini              # Alembic 설정
└── Dockerfile
```

---

## 레이어 구조

요청이 처리되는 순서:

```
HTTP 요청
    ↓
[Router]        - URL 라우팅, 요청/응답 스키마 정의
    ↓
[Dependency]    - 인증 검증 (get_current_user)
    ↓
[Service]       - 비즈니스 로직 (DB 조회/수정)
    ↓
[Model]         - SQLAlchemy ORM 모델 (DB 테이블)
    ↓
PostgreSQL
```

> **원칙**: Router는 얇게, 비즈니스 로직은 Service에 모두 작성합니다.

---

## API 엔드포인트

### 인증 (`/api/auth`)

#### `GET /api/auth/key`
JWT 검증용 대칭키를 반환합니다. Colyseus 서버가 시작 시 이 API를 호출해 키를 가져옵니다.

**응답 예시:**
```json
{
  "key": "your-jwt-secret-string",
  "algorithm": "HS256"
}
```

---

#### `GET /api/auth/login/{provider}`
OAuth 로그인 리다이렉트를 시작합니다.

- `provider`: `google` (현재 구현됨), `naver`, `kakao` (미구현)

**동작**: 해당 OAuth 제공자의 로그인 페이지로 302 리다이렉트

---

#### `GET /api/auth/callback/{provider}`
OAuth 콜백 엔드포인트. 로그인 완료 후 OAuth 제공자가 이 URL로 리다이렉트합니다.

**동작**:
1. OAuth 액세스 토큰 교환
2. 유저 정보 조회
3. DB에 유저 없으면 신규 생성 (`status=NEW`, `rc=UNASSIGNED`)
4. DB에 유저 있으면 `last_login_at` 업데이트
5. JWT 발급 후 `FRONTEND_URL?token=<JWT>`로 리다이렉트

---

### 유저 (`/api/users`)

> 모든 엔드포인트는 `Authorization: Bearer <JWT>` 헤더 필요

#### `GET /api/users/me`
현재 로그인한 유저 정보를 반환합니다.

**응답 예시:**
```json
{
  "id": 1,
  "email": "user@handong.ac.kr",
  "nickname": "홍길동",
  "real_name": "홍길동",
  "auth_provider": "GOOGLE",
  "rc": "UNASSIGNED",
  "status": "NEW",
  "student_id": null,
  "major": null,
  "phone_number": null,
  "instagram_id": null,
  "mbti": null
}
```

---

#### `PATCH /api/users/me/rc`
유저의 RC(기숙사)를 업데이트합니다.

**요청 바디:**
```json
{
  "rc": "Torrey"
}
```

---

#### `PATCH /api/users/me/initialize`
신규 유저(`status=NEW`) 초기 정보를 설정합니다. 완료 후 `status`가 `ACTIVE`로 변경됩니다.

**요청 바디:**
```json
{
  "rc": "Kuyper",
  "student_id": "22000001",
  "major": "전산전자공학부",
  "phone_number": "010-1234-5678",
  "instagram_id": "my_instagram",
  "mbti": "INTJ"
}
```

> `rc`는 필수, 나머지는 선택 입력입니다.

---

## 인증 흐름

### 신규 유저 최초 로그인

```
1. 클라이언트: GET /api/auth/login/google
2. 구글 로그인 페이지로 이동
3. 로그인 완료 → 서버: GET /api/auth/callback/google
4. DB에 유저 없음 → 신규 유저 생성 (status=NEW, rc=UNASSIGNED)
5. JWT 발급 → 클라이언트에 토큰 전달
6. 클라이언트: PATCH /api/users/me/initialize  (RC, 학번 등 초기 설정)
7. 이후 status=ACTIVE로 변경
```

### 기존 유저 재로그인

```
1~5 동일
4. DB에 유저 있음 → last_login_at 업데이트
5. JWT 발급 → 클라이언트에 토큰 전달
```

### JWT 구조

현재 `HS256` 알고리즘(대칭키) 사용합니다.

```json
{
  "sub": "1",        // 유저 ID
  "exp": 1234567890  // 만료 시간 (기본 24시간)
}
```

> **TODO**: Colyseus 서버는 현재 `RS256`(비대칭키) 검증 코드가 작성되어 있으나,
> FastAPI는 `HS256`(대칭키)으로 토큰을 발급합니다. `/api/auth/key` API로
> 대칭키를 공유하는 방식을 사용합니다.

---

## 데이터베이스 모델

### `users` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | 자동 증가 |
| `email` | String(255) | 이메일 (nullable) |
| `nickname` | String(50) | 닉네임 |
| `real_name` | String(50) | 실명 |
| `password_hash` | String(255) | 비밀번호 해시 (LOCAL 인증 시) |
| `auth_provider` | Enum | 인증 제공자 (GOOGLE/NAVER/KAKAO/LOCAL) |
| `rc` | Enum | 기숙사 RC |
| `status` | Enum | 계정 상태 |
| `created_at` | DateTime | 생성 시각 |
| `last_login_at` | DateTime | 마지막 로그인 시각 |
| `last_room_id` | BigInt FK | 마지막으로 있었던 방 |
| `last_room_x` | Int | 마지막 위치 X |
| `last_room_y` | Int | 마지막 위치 Y |
| `student_id` | String(50) | 학번 |
| `major` | String(100) | 전공 |
| `phone_number` | String(20) | 전화번호 |
| `instagram_id` | String(100) | 인스타그램 ID |
| `mbti` | Enum | MBTI |

**복합 유니크 인덱스**: `(email, auth_provider)` → 같은 이메일이라도 다른 OAuth 제공자면 별개 계정

---

### `teams` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | 자동 증가 |
| `name` | String(50) UNIQUE | 팀 이름 |
| `owner_user_id` | BigInt FK → users.id | 소유자 |
| `created_at` | DateTime | 생성 시각 |

---

### `rooms` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | 자동 증가 |
| `room_type` | Enum | 방 유형 (GENERAL/CUSTOM/BUILDING) |
| `name` | String(50) | 방 이름 |
| `owner_type` | Enum | 소유자 유형 (USER/TEAM/SYSTEM) |
| `owner_id` | BigInt | 소유자 ID (owner_type에 따라 다름) |
| `is_public` | Boolean | 공개 여부 |
| `password_hash` | String(255) | 비공개 방 비밀번호 |
| `width` | Int | 맵 너비 |
| `height` | Int | 맵 높이 |
| `created_at` | DateTime | 생성 시각 |
| `updated_at` | DateTime | 수정 시각 |

---

### `room_tiles` 테이블

방 바닥 타일 배치 정보.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | |
| `room_id` | BigInt FK → rooms.id | |
| `x` | Int | 타일 X 좌표 |
| `y` | Int | 타일 Y 좌표 |
| `tile_asset_id` | BigInt | 사용할 타일 에셋 ID |

**복합 유니크**: `(room_id, x, y)` → 같은 위치에 타일 중복 불가

---

### `room_objects` 테이블

방에 배치된 오브젝트 정보.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | |
| `room_id` | BigInt FK → rooms.id | |
| `x` | Int | 오브젝트 X 좌표 |
| `y` | Int | 오브젝트 Y 좌표 |
| `object_asset_id` | String(100) | 오브젝트 에셋 ID |

---

### `room_portals` 테이블

방과 방을 연결하는 포털.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | |
| `from_room_id` | BigInt FK → rooms.id | 출발 방 |
| `from_x` | Int | 포털 위치 X |
| `from_y` | Int | 포털 위치 Y |
| `to_room_id` | BigInt FK → rooms.id | 도착 방 |

---

### `room_roles` 테이블

유저-방 역할 관계 (복합 기본키).

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `room_id` | BigInt FK (PK) | |
| `user_id` | BigInt FK (PK) | |
| `role` | Enum | OWNER / EDITOR / VISITOR |
| `created_at` | DateTime | |

---

### `friends` 테이블

유저 간 친구 관계.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BigInt PK | |
| `user_id` | BigInt FK → users.id | 요청자 |
| `friend_user_id` | BigInt FK → users.id | 대상자 |
| `status` | Enum | PENDING / ACCEPTED / BLOCKED |
| `created_at` | DateTime | |

**복합 유니크**: `(user_id, friend_user_id)` → 중복 친구 요청 방지

---

## Enum 정의

| Enum | 값 |
|------|----|
| `AuthProvider` | `GOOGLE`, `NAVER`, `KAKAO`, `LOCAL` |
| `RC` | `UNASSIGNED`, `Torrey`, `JangGiRyeo`, `Kuyper`, `SonYangWon`, `Philadelphos`, `Carmichael` |
| `UserStatus` | `NEW`, `ACTIVE`, `SUSPENDED`, `DELETED`, `GUEST` |
| `RoomType` | `GENERAL`, `CUSTOM`, `BUILDING` |
| `OwnerType` | `USER`, `TEAM`, `SYSTEM` |
| `RoomRoleType` | `OWNER`, `EDITOR`, `VISITOR` |
| `FriendStatus` | `PENDING`, `ACCEPTED`, `BLOCKED` |
| `MBTI` | `ISTJ` ~ `ENTJ` (16가지) |

---

## 환경변수

`fastapi-backend/.env` 파일에 설정합니다. (Docker 사용 시 `docker-compose.yml`에서 주입)

```env
# DB
DATABASE_URL=postgresql://team_admin:<DB_PASSWORD>@localhost:5432/metaverse_db
DB_PASSWORD=your_db_password

# JWT
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# 세션 미들웨어
SECRET_KEY=your_secret_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# URL
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

---

## 로컬 실행 방법

### 사전 준비
- Python 3.11+
- uv 패키지 매니저 ([설치 방법](https://docs.astral.sh/uv/))
- PostgreSQL 실행 중

### 실행

```bash
cd fastapi-backend

# 의존성 설치
uv sync

# .env 파일 작성 (위 환경변수 참고)
cp .env.example .env  # 없으면 직접 생성

# 서버 실행
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 시작 후 `http://localhost:8000/docs` 에서 Swagger UI 확인 가능.

---

## DB 마이그레이션

Alembic을 사용합니다.

```bash
cd fastapi-backend

# 현재 마이그레이션 상태 확인
uv run alembic current

# 최신 버전으로 업그레이드
uv run alembic upgrade head

# 새 마이그레이션 파일 자동 생성 (모델 변경 후)
uv run alembic revision --autogenerate -m "변경 내용 설명"

# 한 단계 롤백
uv run alembic downgrade -1
```

> **주의**: `models.py`를 변경한 후에는 반드시 마이그레이션 파일을 생성하고 적용해야 합니다.

---

## 새 기능 추가 방법

### 1. 새 API 엔드포인트 추가

예시: "방 목록 조회" API 추가

**Step 1** - 스키마 정의 (`app/schemas/room.py` 생성):
```python
from pydantic import BaseModel

class RoomResponse(BaseModel):
    id: int
    name: str
    room_type: str

    class Config:
        from_attributes = True
```

**Step 2** - 서비스 로직 작성 (`app/services/room_service.py` 생성):
```python
from sqlalchemy.orm import Session
from app.db.models import Room

class RoomService:
    def __init__(self, db: Session):
        self.db = db

    def get_rooms(self):
        return self.db.query(Room).all()
```

**Step 3** - 라우터 작성 (`app/routers/room.py` 생성):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.room_service import RoomService
from app.schemas.room import RoomResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    return RoomService(db).get_rooms()
```

**Step 4** - `app/main.py`에 라우터 등록:
```python
from app.routers import room
app.include_router(room.router, prefix="/api", tags=["rooms"])
```

### 2. 새 DB 모델 추가

`app/db/models.py`에 클래스 추가 후 마이그레이션 실행:

```bash
uv run alembic revision --autogenerate -m "add rooms table"
uv run alembic upgrade head
```
