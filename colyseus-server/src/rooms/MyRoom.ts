import { Room, Client } from "@colyseus/core";
import { MyRoomState, Player } from "./schema/MyRoomState";
import * as jwt from "jsonwebtoken";
import { ServerGlobal } from "../app.config";

export class MyRoom extends Room<MyRoomState> {
  maxClients = 4;

  /*
  방에 들어올 때 이 함수가 실행되므로
  유니티에서 client.JoinOrCreate("room_name", options) 이 함수를 실행할 때, option에 jwt를 넣을 것
  */
  async onAuth(client: Client, options: any, request?: any) {
    const token = options.token;

    if (!token) {
      console.error("token not find");
      return false;
    }

    try {
      const decoded = jwt.verify(token, ServerGlobal.publicKey.key, {
        algorithms: [ServerGlobal.publicKey.algorithm],
      }) as any;

      //todo: jwt payload에 뭘 넣을지에 따라 달라져야함
      return {
        userId: decoded.sub,
        nickname: decoded.nickname,
        role: decoded.role,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown Error";
      console.error("Authentication failed:", errorMessage);
      return false;
    }
  }

  onCreate (options: any) {
    //this.setState(new MyRoomState()); < 이 표현 방식은 deprecated됨
    this.state = new MyRoomState();

    this.onMessage("move", (client, input) => {
      const player = this.state.players.get(client.sessionId);
      if (player) {
        player.inputX = input.x;
        player.inputY = input.y;
      }
    });

    this.setSimulationInterval((deltaTime) => this.update(deltaTime));
  }


  update(deltaTime: number) {
    this.state.players.forEach((player) => {
      let inputX = player.inputX;
      let inputY = player.inputY;

      // Normalize if magnitude > 1 (to prevent faster diagonal movement)
      const magnitude = Math.sqrt(inputX * inputX + inputY * inputY);
      if (magnitude > 1) {
        inputX /= magnitude;
        inputY /= magnitude;
      }

      // Update position
      // speed is in units per second, so we multiply by deltaTime (in ms) / 1000
      player.x += inputX * player.speed * (deltaTime / 1000);
      player.y += inputY * player.speed * (deltaTime / 1000);
    });
  }

  onJoin(client: Client, options: any) {
    console.log(client.sessionId, "joined!");
    this.state.players.set(client.sessionId, new Player());
  }

  onLeave(client: Client, consented: boolean) {
    console.log(client.sessionId, "left!");
    this.state.players.delete(client.sessionId);
  }

  onDispose() {
    console.log("room", this.roomId, "disposing...");
  }
}
