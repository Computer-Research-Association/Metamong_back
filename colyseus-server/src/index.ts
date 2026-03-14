/**
 * IMPORTANT:
 * ---------
 * Do not manually edit this file if you'd like to host your server on Colyseus Cloud
 *
 * If you're self-hosting (without Colyseus Cloud), you can manually
 * instantiate a Colyseus Server as documented here:
 *
 * See: https://docs.colyseus.io/server/api/#constructor-options
 */
import dotenv from "dotenv";
// 루트 .env 우선 로드 (로컬 개발용). Docker에서는 environment: 섹션이 우선하므로 영향 없음
dotenv.config({ path: "../.env" });
dotenv.config({ path: ".env" }); // 로컬 오버라이드 (colyseus-server/.env 가 있으면 적용)

import { listen } from "@colyseus/tools";

// Import Colyseus config
import app from "./app.config";

// Create and listen on 2567 (or PORT environment variable.)
listen(app);
