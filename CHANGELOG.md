# Changelog

이 프로젝트의 모든 주요 변경사항을 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따르며,
버전 관리는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다.

---

## [Unreleased]

### Added

- FastAPI REST API 서버 초기 구성
- Colyseus 실시간 게임 서버 초기 구성
- Google OAuth 2.0 로그인
- JWT 발급 및 검증 (HS256)
- 유저 초기 정보 설정 API (`PATCH /api/users/me/initialize`)
- RC(기숙사) 업데이트 API (`PATCH /api/users/me/rc`)
- 대칭키 공유 API (`GET /api/auth/key`)
- 실시간 플레이어 이동 동기화 (Colyseus `my_room`)
- Docker Compose 기반 전체 서비스 배포 구성
- GitHub Actions CI/CD 자동 배포 파이프라인
- 프로젝트 문서화 (`documents/` 폴더)

---

<!-- 새 버전을 릴리즈할 때 아래 형식을 복사해서 위에 추가하세요 -->
<!--
## [x.y.z] - YYYY-MM-DD

### Added
- 새로 추가된 기능

### Changed
- 기존 기능의 변경사항

### Deprecated
- 곧 제거될 예정인 기능

### Removed
- 이번 버전에서 제거된 기능

### Fixed
- 버그 수정

### Security
- 보안 관련 수정
-->
