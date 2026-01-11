## 📄 migrations/README.md

# 🗄️ Database Migration Guide (Alembic)

이 폴더는 **Alembic**을 사용하여 데이터베이스 스키마의 변경 사항을 관리하는 공간입니다.
모든 모델(`app/db/models.py`)의 변경 사항은 반드시 마이그레이션 파일을 통해 실제 DB에 반영되어야 합니다.

---

## 🚀 빠른 시작 (Quick Workflow)

모델을 수정하고 DB에 반영하는 표준 절차입니다.

### 1. 전제 조건

- 로컬에서 Docker DB 컨테이너가 실행 중이어야 합니다. (`docker compose up -d db`)
- `.env` 파일의 `DATABASE_URL`이 `localhost:5432`를 바라보고 있어야 합니다.

### 2. 마이그레이션 파일 생성 (Revision)

`models.py`에서 컬럼을 추가하거나 수정했다면 다음 명령어를 입력하세요.

```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"

```

- `migrations/versions/` 폴더 내에 새로운 `.py` 파일이 생성됩니다.
- **중요:** 생성된 파일을 열어 `upgrade`와 `downgrade` 함수가 의도대로 작성되었는지 꼭 확인하세요.

### 3. DB에 반영 (Upgrade)

작성된 마이그레이션 코드를 실제 DB에 적용합니다.

```bash
uv run alembic upgrade head

```

---

## 🛠️ 주요 명령어 모음

| 명령어                        | 설명                                  |
| ----------------------------- | ------------------------------------- |
| `uv run alembic history`      | 현재까지의 마이그레이션 히스토리 확인 |
| `uv run alembic current`      | 현재 DB에 적용된 버전 확인            |
| `uv run alembic upgrade head` | 가장 최신 버전으로 DB 업데이트        |
| `uv run alembic downgrade -1` | 한 단계 이전 버전으로 되돌리기        |

---

## ⚠️ 팀 협업 시 주의사항 (Best Practices)

1. **병합 충돌(Merge Conflict):** \* 두 명이 동시에 각자의 브랜치에서 마이그레이션 파일을 만들면 충돌이 발생할 수 있습니다.

- `git pull` 이후 마이그레이션 파일이 새로 들어왔다면, 반드시 `uv run alembic upgrade head`를 먼저 실행하세요.

2. **코드 리뷰:** _ PR 시 마이그레이션 파일(`migrations/versions/_.py`)도 포함되어야 합니다.

- 리뷰어는 새 컬럼의 `nullable` 여부나 인덱스 추가 등을 확인해 주세요.

3. **환경 변수:** \* `env.py`는 `app.core.config.settings`를 사용하여 접속 정보를 가져옵니다.

- 직접 `alembic.ini` 파일의 접속 주소를 수정하지 마세요.

---
