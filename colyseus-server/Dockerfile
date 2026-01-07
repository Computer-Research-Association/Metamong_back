# 1. 빌드 단계
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm ci

# 소스 복사 및 빌드 (TypeScript -> JavaScript)
COPY . .
RUN npm run build

# 2. 실행 단계 (runtime)
FROM node:20-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production

# devDependencies 제외한런타임 의존성만 재설치
COPY package*.json ./
RUN npm ci --omit=dev

# 빌드 산출물 복사
COPY --from=builder /app/build ./build

# Colyseus 기본 포트
EXPOSE 2567

# 서버 실행
CMD ["npm", "start"]