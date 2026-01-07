이 파일은 `fastapi-backend/README_UV.md`로 저장하거나 프로젝트 메인 `README.md`에 포함하여 팀원들에게 공유하세요. Java/Node.js 개발자들의 눈높이에 맞춰 작성되었습니다.

---

# FastAPI 개발 환경 가이드 (uv 기반)

이 프로젝트는 Python의 패키지 및 버전 관리 도구로 **`uv`**를 사용합니다. `uv`는 Node.js의 `npm/bun`, Java의 `Gradle`과 유사한 역할을 하며, 매우 빠른 속도와 일관된 환경을 제공합니다.

---

## 1. 설치

[uv 깃허브](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) 에서 installation 방법 숙지 후 설치

---

## 2. 프로젝트 시작하기 (Clone 후)

리포지토리를 클론 받은 후, `fastapi-backend` 폴더에서 아래 명령어를 실행하세요. **별도로 Python을 설치할 필요가 없습니다.** `uv`가 설정된 Python 버전(3.11+)을 알아서 다운로드하고 가상환경을 구축합니다.

```bash
cd fastapi-backend

# 1. 의존성 설치 및 가상환경(.venv) 생성
uv sync

# 2. 서버 실행
uv run uvicorn main:app --reload

```

---

## 3. 명령어 매핑 (Cheat Sheet)

익숙한 프레임워크의 명령어와 비교하여 사용하세요.

| 기능                   | **uv (Python)**     | **npm (Node.js)**     | **Gradle (Java)**   |
| ---------------------- | ------------------- | --------------------- | ------------------- |
| **의존성 설치**        | `uv sync`           | `npm install`         | `./gradlew build`   |
| **패키지 추가**        | `uv add [pkg]`      | `npm install [pkg]`   | `build.gradle` 수정 |
| **패키지 제거**        | `uv remove [pkg]`   | `npm uninstall [pkg]` | `build.gradle` 수정 |
| **서버 실행**          | `uv run uvicorn...` | `npm start`           | `./gradlew bootRun` |
| **임의 스크립트 실행** | `uv run [file].py`  | `node [file].js`      | -                   |

---

## 4. 주요 파일 설명

- **`pyproject.toml`**: 프로젝트 설정 및 메인 의존성 명세서 (Spring의 `build.gradle`, Node의 `package.json` 역할)
- **`uv.lock`**: 설치된 패키지의 상세 버전 고정 파일 (Node의 `package-lock.json` 역할, **Git에 반드시 포함**)
- **`.venv/`**: 프로젝트 전용 가상환경 폴더 (Node의 `node_modules`와 유사, **Git 제외**)

---

## 5. IDE 설정 (필수)

VS Code나 PyCharm에서 라이브러리 인식(Auto-complete)이 안 된다면 아래 설정을 확인하세요.

1. **VS Code:** `Command + Shift + P` -> `Python: Select Interpreter` -> **`./venv/bin/python`** 선택
2. **PyCharm:** `Settings` -> `Project` -> `Python Interpreter` -> `Add Interpreter` -> `Existing environment`에서 프로젝트 폴더 내의 `.venv` 선택

---

## 6. ⚠️ 주의사항 (Java/Node 개발자 필독)

1. **들여쓰기(Indentation)가 곧 코드 블록입니다.**

- Java/Node처럼 `{}`가 없습니다. 들여쓰기 한 칸만 틀려도 코드가 작동하지 않거나 논리 에러가 발생합니다. (Tab 대신 스페이스 4칸 권장)

2. **`uv run`을 생활화하세요.**

- 단순히 `python main.py`를 치면 시스템 파이썬을 바라볼 수 있습니다. 반드시 `uv run`을 앞에 붙여서 프로젝트 가상환경 내에서 실행되도록 하세요.

3. **비동기 처리 (`async`/`await`)**

- FastAPI의 엔드포인트는 기본적으로 `async def`로 선언합니다. DB 접근 등 I/O 작업 시 반드시 `await`를 확인하세요.

4. **타입 힌트 활용**

- Python은 동적 타입이지만, FastAPI는 Java처럼 타입을 명시해야 합니다. `def root(item_id: int):` 처럼 타입을 적어주어야 Swagger 문서가 자동 생성됩니다.

---

### 💡 새로운 패키지가 필요할 땐?

팀원 중 누구나 새로운 라이브러리가 필요하면 아래 명령어를 치고 생성된 `pyproject.toml`과 `uv.lock`을 커밋하면 됩니다.

```bash
uv add sqlalchemy  # 예: SQLAlchemy 추가 시

```

---
