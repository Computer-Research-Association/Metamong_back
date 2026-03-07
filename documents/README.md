# Metamong 백엔드 프로젝트 개요

한동대학교 메타버스 플랫폼(Metamong)의 백엔드 서버 문서입니다.

---

## 목차

| 문서 | 설명 |
|------|------|
| [README.md](./README.md) | 프로젝트 전체 개요 (현재 문서) |
| [fastapi-backend.md](./fastapi-backend.md) | FastAPI REST API 서버 구조 및 유지보수 가이드 |
| [colyseus-server.md](./colyseus-server.md) | Colyseus 실시간 게임 서버 구조 및 유지보수 가이드 |
| [deployment.md](./deployment.md) | Docker 배포 및 CI/CD 가이드 |

---

## 아키텍처 개요

```
[Unity WebGL 클라이언트]
        |
        |  HTTPS (REST API)       WebSocket
        |__________________________|
        |                          |
   [FastAPI :8000]          [Colyseus :2567]
        |                          |
   [PostgreSQL :5432]          (상태 관리)
```

### 서버 구성

| 서버 | 기술 스택 | 역할 | 포트 |
|------|-----------|------|------|
| FastAPI Backend | Python 3.11, FastAPI, SQLAlchemy | REST API, 인증(OAuth), DB 관리 | 8000 |
| Colyseus Server | Node.js 20, Colyseus 0.16, TypeScript | 실시간 멀티플레이어 게임 상태 동기화 | 2567 |
| PostgreSQL | postgres:15 | 영구 데이터 저장 | 5432 |

---

## 클라이언트 연동 흐름

### 1. 로그인 및 JWT 발급
```
클라이언트 → GET /api/auth/login/google
           → 구글 로그인 페이지 리다이렉트
           → 로그인 완료 후 콜백
           → GET /api/auth/callback/google
           → JWT 토큰 발급 → FRONTEND_URL?token=<JWT>
```

### 2. 실시간 서버 입장
```
클라이언트 → GET /api/auth/key        (대칭키 요청)
           → Colyseus JoinOrCreate("my_room", { token: <JWT> })
           → onAuth에서 JWT 검증
           → 입장 성공 시 실시간 상태 동기화 시작
```

---

## 리포지토리 구조

```
Metamong_back/
├── colyseus-server/         # Colyseus 실시간 서버 (Node.js + TypeScript)
├── fastapi-backend/         # FastAPI REST API 서버 (Python)
├── documents/               # 프로젝트 문서 (현재 폴더)
├── docker-compose.yml       # 전체 서비스 오케스트레이션
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions CI/CD
└── README.md
```

---

## 환경변수 목록

배포 시 `.env` 파일 또는 GitHub Secrets에 아래 값을 설정해야 합니다.

| 변수명 | 용도 |
|--------|------|
| `DB_PASSWORD` | PostgreSQL 비밀번호 |
| `JWT_SECRET` | JWT 서명용 대칭키 (FastAPI ↔ Colyseus 공유) |
| `GOOGLE_CLIENT_ID` | Google OAuth 클라이언트 ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 클라이언트 Secret |
| `BACKEND_URL` | FastAPI 서버 공개 URL (OAuth 콜백에 사용) |
| `FRONTEND_URL` | Unity WebGL 클라이언트가 호스팅되는 URL |
| `SECRET_KEY` | Starlette 세션 미들웨어 시크릿 키 |

> 자세한 배포 방법은 [deployment.md](./deployment.md)를 참고하세요.
