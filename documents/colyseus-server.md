# Colyseus 실시간 서버 가이드

Unity 클라이언트와 WebSocket으로 연결되는 실시간 멀티플레이어 게임 서버입니다.

---

## 목차

1. [기술 스택](#기술-스택)
2. [디렉토리 구조](#디렉토리-구조)
3. [Colyseus 핵심 개념](#colyseus-핵심-개념)
4. [현재 구현 상태](#현재-구현-상태)
5. [MyRoom 상세 분석](#myroom-상세-분석)
6. [상태 스키마](#상태-스키마)
7. [인증 흐름](#인증-흐름)
8. [환경변수](#환경변수)
9. [로컬 실행 방법](#로컬-실행-방법)
10. [새 기능 추가 방법](#새-기능-추가-방법)
11. [디버깅 도구](#디버깅-도구)

---

## 기술 스택

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| Node.js | >= 20.9.0 | 런타임 |
| TypeScript | ^5.0 | 언어 |
| Colyseus | ^0.16 | 게임 서버 프레임워크 |
| @colyseus/tools | ^0.16 | 서버 설정 유틸리티 |
| @colyseus/schema | (colyseus 내장) | 상태 직렬화/동기화 |
| @colyseus/monitor | ^0.16 | 서버 모니터링 대시보드 |
| @colyseus/playground | ^0.16 | 개발용 테스트 UI |
| jsonwebtoken | ^9.0 | JWT 검증 |
| express | ^4.18 | HTTP 라우팅 |

---

## 디렉토리 구조

```
colyseus-server/
├── src/
│   ├── index.ts              # 진입점 - 서버 시작
│   ├── app.config.ts         # 서버 설정, Room 등록, Express 라우트
│   └── rooms/
│       ├── MyRoom.ts         # 게임 룸 로직 (인증, 입장, 상태 업데이트)
│       └── schema/
│           ├── MyRoomState.ts # 룸 상태 스키마 (동기화 대상)
│           └── MapState.ts    # 맵 상태 스키마 (현재 미사용)
├── loadtest/
│   └── example.ts            # 부하 테스트 스크립트
├── test/
│   └── MyRoom_test.ts        # 룸 단위 테스트
├── package.json
├── tsconfig.json
├── ecosystem.config.cjs      # PM2 프로세스 설정 (직접 실행 시)
└── Dockerfile
```

---

## Colyseus 핵심 개념

### Room (방)

Colyseus의 핵심 단위입니다. 각 방은 독립적인 게임 세션이며:
- 클라이언트가 `JoinOrCreate()` 호출 시 방이 없으면 생성, 있으면 입장
- 각 방은 **State**(상태)를 보유하며, 변경 사항이 자동으로 모든 클라이언트에게 동기화됨
- 방이 비면 자동으로 제거됨

### Schema (스키마)

`@colyseus/schema`로 정의된 클래스는 상태 동기화 대상입니다.
- `@type("number")` 등의 데코레이터로 동기화할 필드를 지정
- **데코레이터가 없는 필드**는 서버에만 존재하고 클라이언트에 전송되지 않음

### Room 생명주기

```
onCreate()   - 방 최초 생성 시 (상태 초기화, 메시지 핸들러 등록)
    ↓
onAuth()     - 클라이언트 인증 (JWT 검증 등)
    ↓
onJoin()     - 인증 통과한 클라이언트 입장
    ↓
  [게임 진행 - 메시지 수신 / 상태 업데이트]
    ↓
onLeave()    - 클라이언트 퇴장
    ↓
onDispose()  - 방의 마지막 클라이언트가 떠날 때 방 제거
```

---

## 현재 구현 상태

현재 `my_room` 하나의 룸이 구현되어 있습니다.

| 기능 | 구현 여부 |
|------|-----------|
| JWT 인증 (onAuth) | 구현됨 (현재 publicKey 로드 로직 주석 처리) |
| 플레이어 입장/퇴장 | 구현됨 |
| 플레이어 이동 (input 메시지) | 구현됨 |
| 서버 사이드 이동 계산 | 구현됨 |
| 방 최대 인원 | 4명 |
| `/api/auth/key` 연동 | 미구현 (주석 처리, TODO) |

---

## MyRoom 상세 분석

`src/rooms/MyRoom.ts`

### `onAuth(client, options, request)` - 입장 전 인증

클라이언트가 방에 입장하기 전에 실행됩니다.

```typescript
// Unity 클라이언트에서 이렇게 호출해야 함:
// client.JoinOrCreate("my_room", new { token = jwtToken })
```

- `options.token`에서 JWT를 추출
- `jwt.verify(token, publicKey, { algorithms: ["RS256"] })`로 검증
- 성공 시 `{ userId, nickname, role }` 반환 → `onJoin`의 `auth` 파라미터로 전달
- 실패 시 `false` 반환 → 클라이언트 입장 거부

> **현재 상태**: `ServerGlobal.publicKey`가 비어 있어 모든 인증이 실패합니다.
> `app.config.ts`의 주석 처리된 코드를 활성화하거나, 대칭키 방식으로 변경해야 합니다.

### `onCreate(options)` - 방 초기화

```typescript
this.state = new MyRoomState();  // 상태 초기화

// "input" 메시지 핸들러 등록
this.onMessage("input", (client, input) => {
    const player = this.state.players.get(client.sessionId);
    if (player) {
        player.inputX = input.x;  // inputX/Y는 동기화 안 됨 (서버 내부용)
        player.inputY = input.y;
    }
});

// 게임 루프 시작 (매 프레임 update 호출)
this.setSimulationInterval((deltaTime) => this.update(deltaTime));
```

### `update(deltaTime)` - 게임 루프

매 프레임 실행되며 플레이어 위치를 업데이트합니다.

```
입력 → 정규화(대각선 이동 속도 보정) → 위치 계산 → 상태 업데이트 → 자동 동기화
```

- `speed = 200` (units/second)
- `x += inputX * speed * (deltaTime / 1000)`
- 변경된 `x`, `y`는 자동으로 클라이언트에 동기화됨

### `onJoin(client, options)` - 입장

```typescript
this.state.players.set(client.sessionId, new Player());
// sessionId를 키로 플레이어 추가
```

### `onLeave(client, consented)` - 퇴장

```typescript
this.state.players.delete(client.sessionId);
```

---

## 상태 스키마

### `MyRoomState`

```typescript
class MyRoomState extends Schema {
    @type({ map: Player }) players = new MapSchema<Player>();
}
```

- `players`: `sessionId → Player` 맵. 클라이언트에게 동기화됨

### `Player`

| 필드 | 타입 | 동기화 | 설명 |
|------|------|--------|------|
| `x` | number | O | 현재 X 위치 |
| `y` | number | O | 현재 Y 위치 |
| `speed` | number | O | 이동 속도 (기본: 200) |
| `inputX` | number | X | 이동 입력 X (서버 내부용) |
| `inputY` | number | X | 이동 입력 Y (서버 내부용) |

> `inputX`, `inputY`는 `@type` 데코레이터가 없으므로 클라이언트에 전송되지 않습니다.

### `MapState` (현재 미사용)

```typescript
class MapState extends Schema {
    @type("int32") width: number = 0;
    @type("int32") height: number = 0;
}
```

맵 크기 동기화용으로 선언되어 있으나 아직 사용되지 않습니다.

---

## 인증 흐름

### 현재 구조 (대칭키 방식 예정)

```
[FastAPI] JWT 발급 (HS256, JWT_SECRET 사용)
    ↓
[클라이언트] JWT 보관
    ↓
[Colyseus 시작 시] GET /api/auth/key → JWT_SECRET 수신 → ServerGlobal.publicKey에 저장
    ↓
[클라이언트 입장 시] JoinOrCreate("my_room", { token: JWT })
    ↓
[Colyseus onAuth] jwt.verify(token, ServerGlobal.publicKey) 검증
```

### 활성화 방법

`app.config.ts`의 주석 처리된 코드를 해제하고 URL을 수정합니다:

```typescript
initializeGameServer: async (gameServer) => {
    try {
        const response = await axios.get(`${process.env.API_URL}/api/auth/key`);
        ServerGlobal.publicKey = response.data.key;
        console.log("JWT key loaded");
    } catch (error) {
        console.error("Failed to load JWT key");
        process.exit(1);
    }
    gameServer.define('my_room', MyRoom);
},
```

또한 `MyRoom.ts`의 `onAuth`에서 알고리즘을 `HS256`으로 변경:

```typescript
const decoded = jwt.verify(token, ServerGlobal.publicKey, {
    algorithms: ["HS256"],  // RS256 → HS256
}) as any;
```

---

## 환경변수

`colyseus-server/.env` 또는 Docker 환경:

```env
API_URL=http://fastapi:8000      # FastAPI 서버 URL (Docker 내부)
JWT_SECRET=your_jwt_secret       # JWT 검증키
NODE_ENV=production              # production이면 playground 비활성화
PORT=2567                        # Colyseus 기본 포트
```

---

## 로컬 실행 방법

### 사전 준비
- Node.js 20+
- npm

### 실행

```bash
cd colyseus-server

# 의존성 설치
npm install

# 개발 서버 실행 (파일 변경 시 자동 재시작)
npm start
```

서버 시작 후:
- **Playground UI**: `http://localhost:2567/` (개발 환경만 접근 가능)
- **Monitor 대시보드**: `http://localhost:2567/monitor`

### 테스트

```bash
# 단위 테스트
npm test

# 부하 테스트 (2개 클라이언트로 my_room 부하 테스트)
npm run loadtest
```

### 빌드 (프로덕션)

```bash
npm run build
# build/ 폴더에 JavaScript 파일 생성
```

---

## 새 기능 추가 방법

### 1. 새 메시지 타입 추가

예시: 채팅 메시지 처리

`MyRoom.ts`의 `onCreate`에 추가:

```typescript
this.onMessage("chat", (client, message) => {
    // 모든 클라이언트에게 브로드캐스트
    this.broadcast("chat", {
        sender: client.sessionId,
        text: message.text,
        timestamp: Date.now()
    });
});
```

Unity 클라이언트에서:
```csharp
room.Send("chat", new { text = "안녕하세요!" });
```

### 2. 새 상태 필드 추가

예시: 플레이어에 닉네임 추가

`schema/MyRoomState.ts` 수정:

```typescript
export class Player extends Schema {
    @type("number") x: number = 0;
    @type("number") y: number = 0;
    @type("number") speed: number = 200;
    @type("string") nickname: string = "";  // 추가

    inputX: number = 0;
    inputY: number = 0;
}
```

`MyRoom.ts`의 `onJoin`에서 설정:

```typescript
onJoin(client: Client, options: any, auth: any) {
    const player = new Player();
    player.nickname = auth?.nickname ?? "Guest";  // onAuth 반환값 활용
    this.state.players.set(client.sessionId, player);
}
```

### 3. 새 룸 타입 추가

예시: 회의실 룸 추가

**Step 1** - `src/rooms/MeetingRoom.ts` 생성:

```typescript
import { Room, Client } from "@colyseus/core";
import { MeetingRoomState } from "./schema/MeetingRoomState";

export class MeetingRoom extends Room<MeetingRoomState> {
    maxClients = 20;

    onCreate(options: any) {
        this.state = new MeetingRoomState();
    }

    onJoin(client: Client, options: any) { ... }
    onLeave(client: Client, consented: boolean) { ... }
}
```

**Step 2** - `app.config.ts`에 룸 등록:

```typescript
import { MeetingRoom } from "./rooms/MeetingRoom";

gameServer.define('meeting_room', MeetingRoom);
```

---

## 디버깅 도구

### Colyseus Monitor

`http://localhost:2567/monitor` 에서 확인 가능:
- 현재 활성화된 방 목록
- 각 방의 클라이언트 수
- 방 상태(State) 실시간 조회

> 프로덕션에서는 비밀번호로 보호하는 것을 권장합니다.
> [공식 문서 참고](https://docs.colyseus.io/tools/monitor/#restrict-access-to-the-panel-using-a-password)

### Colyseus Playground

개발 환경(`NODE_ENV !== "production"`)에서 `http://localhost:2567/` 접근 시 사용 가능합니다.
브라우저에서 직접 방에 입장하여 메시지를 주고받을 수 있습니다.
