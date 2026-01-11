# 🗄️ Database Migration Guide (Alembic)

이 폴더는 **Alembic**을 사용하여 데이터베이스 스키마의 변경 사항을 관리합니다. 모든 모델(`app/db/models.py`)의 변경 사항은 반드시 마이그레이션 파일을 통해 실제 DB에 반영되어야 합니다.

---

## 🚀 표준 워크플로우 (Standard Workflow)

### 1. 전제 조건

- 로컬 DB 컨테이너 실행 중 (`docker compose up -d db`)
- `.env` 설정 확인 (`DATABASE_URL=postgresql://...` 이 `localhost`를 바라봐야 함)

### 2. 명령어 순서

1. **코드 수정**: `app/db/models.py`에서 테이블이나 컬럼 수정
2. **파일 생성**: `uv run alembic revision --autogenerate -m "설명"`
3. **DB 반영**: `uv run alembic upgrade head`

---

## 💡 실전 예시: 유저 모델에 '닉네임' 컬럼 추가하기

새로운 기능을 위해 `User` 모델에 `nickname` 컬럼을 추가해야 한다고 가정해 봅시다.

### Step 1: 모델 수정 (`app/db/models.py`)

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    # 아래와 같이 새로운 컬럼 추가
    nickname = Column(String, unique=True, nullable=True)

```

### Step 2: 마이그레이션 파일 생성

터미널에서 아래 명령어를 실행합니다.

```bash
uv run alembic revision --autogenerate -m "Add nickname to users"

```

- `migrations/versions/` 폴더에 `xxxx_add_nickname_to_users.py` 파일이 생성됩니다.

### Step 3: 생성된 파일 검토 (중요!)

생성된 파일을 열어 `upgrade()` 함수 내에 의도한 코드가 있는지 확인합니다.

```python
def upgrade() -> None:
    # Alembic이 자동으로 생성한 코드
    op.add_column('users', sa.Column('nickname', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'users', ['nickname'])

```

### Step 4: 데이터베이스에 적용

```bash
uv run alembic upgrade head

```

- 이제 DB의 `users` 테이블에 실제 `nickname` 컬럼이 생깁니다.

---

## 🛠️ 주요 명령어 모음

| 명령어                        | 설명                                       |
| ----------------------------- | ------------------------------------------ |
| `uv run alembic history`      | 마이그레이션 이력 확인                     |
| `uv run alembic current`      | 현재 DB에 적용된 버전 확인                 |
| `uv run alembic upgrade head` | 최신 버전으로 DB 업데이트 (가장 많이 사용) |
| `uv run alembic downgrade -1` | 직전 버전으로 되돌리기                     |

---

## ⚠️ 협업 시 주의사항

1. **DB 상태 동기화**: `git pull`을 받은 후 새로운 마이그레이션 파일이 있다면, 서버를 켜기 전에 반드시 `uv run alembic upgrade head`를 먼저 실행해 주세요.
2. **파일 검토 필수**: `--autogenerate`는 완벽하지 않습니다. 테이블 이름 변경이나 복잡한 관계 수정 시에는 생성된 코드가 맞는지 꼭 눈으로 확인해야 합니다.
3. **임포트 누락 주의**: 새로운 모델 파일을 만들었다면, `migrations/env.py`에서 해당 모델이 인식되도록 임포트되어 있는지 확인하세요.

---
