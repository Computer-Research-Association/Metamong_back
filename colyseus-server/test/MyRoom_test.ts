import assert from "assert";
import { generateKeyPairSync } from "crypto";
import jwt from "jsonwebtoken";
import { ColyseusTestServer, boot } from "@colyseus/testing";

import appConfig, { ServerGlobal } from "../src/app.config";
import { MyRoomState } from "../src/rooms/schema/MyRoomState";

describe("testing your Colyseus app", () => {
  let colyseus: ColyseusTestServer;

  before(async () => {
    const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });

    ServerGlobal.publicKey = publicKey.export({ type: "pkcs1", format: "pem" }).toString();

    const token = jwt.sign(
      { nickname: "tester", role: "player" },
      privateKey.export({ type: "pkcs1", format: "pem" }).toString(),
      {
        algorithm: "RS256",
        subject: "user-1",
        expiresIn: "1h",
      }
    );

    colyseus = await boot(appConfig);

    // keep token for test scope
    (global as any).__TEST_TOKEN__ = token;
  });

  after(async () => {
    delete (global as any).__TEST_TOKEN__;
    await colyseus.shutdown();
  });

  beforeEach(async () => await colyseus.cleanup());

  it("connecting into a room", async () => {
    const room = await colyseus.createRoom<MyRoomState>("my_room", {});

    const client1 = await colyseus.connectTo(room, {
      token: (global as any).__TEST_TOKEN__,
    });

    assert.strictEqual(client1.sessionId, room.clients[0].sessionId);

    await room.waitForNextPatch();

    const player = client1.state.players[client1.sessionId];
    assert.ok(player, "player should be added to room state");
    assert.strictEqual(player.x, 0);
    assert.strictEqual(player.y, 0);
    assert.strictEqual(player.speed, 200);
  });
});
