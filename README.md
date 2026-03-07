# Metamong - 한동대학교 메타버스 플랫폼

한동대학교 구성원들이 온라인 가상 공간에서 소통하고 교류할 수 있는 메타버스 플랫폼입니다.

---

## 프로젝트 소개

Metamong은 Unity WebGL로 제작된 클라이언트와 두 개의 백엔드 서버로 구성됩니다.

- 학생들이 아바타로 가상 캠퍼스를 돌아다니며 다른 구성원들과 실시간으로 만날 수 있습니다.
- Google 계정으로 로그인하며, 한동대 RC(기숙사) 소속 정보를 프로필에 등록할 수 있습니다.
- 방(Room)을 생성하고 이동하며, 공간 내 오브젝트 및 타일 배치를 커스터마이징할 수 있습니다.

---

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 클라이언트 | Unity WebGL |
| 실시간 서버 | Node.js, Colyseus 0.16, TypeScript |
| REST API 서버 | Python 3.11, FastAPI |
| 데이터베이스 | PostgreSQL 15 |
| 인증 | Google OAuth 2.0, JWT |
| 배포 | Docker Compose, GitHub Actions |

---

## 서버 구조

```
[Unity WebGL 클라이언트]
        |
        ├── REST API (HTTP)  ──→  FastAPI  :8000  ──→  PostgreSQL :5432
        │                         (로그인, 유저 정보)
        │
        └── WebSocket        ──→  Colyseus :2567
                                  (실시간 위치 동기화)
```

- **FastAPI**: 사용자 인증(Google OAuth), 유저/방 데이터 관리
- **Colyseus**: 플레이어 실시간 이동 및 상태 동기화

---

## 문서

개발 및 유지보수에 필요한 상세 문서는 [`documents/`](./documents/) 폴더에 있습니다.

| 문서 | 설명 |
|------|------|
| [프로젝트 개요](./documents/README.md) | 전체 아키텍처, 환경변수 목록 |
| [FastAPI 서버](./documents/fastapi-backend.md) | API 명세, DB 모델, 인증 흐름 |
| [Colyseus 서버](./documents/colyseus-server.md) | 룸 구조, 상태 동기화, 메시지 처리 |
| [배포 가이드](./documents/deployment.md) | Docker 배포, CI/CD, 트러블슈팅 |
