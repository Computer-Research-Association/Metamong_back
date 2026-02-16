import { Room, Client } from "@colyseus/core";
import { MyRoomState, Player } from "./schema/MyRoomState";

export class MyRoom extends Room<MyRoomState> {
  maxClients = 4;

  onCreate (options: any) {
    this.setState(new MyRoomState());

    this.onMessage("input", (client, input) => {
      const player = this.state.players.get(client.sessionId);
      if (player) {
        player.inputX = input.x;
        player.inputY = input.y;
      }
    });

    this.setSimulationInterval((deltaTime) => this.update(deltaTime));
  }

  update(deltaTime: number) {
    this.state.players.forEach(player => {
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

  onJoin (client: Client, options: any) {
    console.log(client.sessionId, "joined!");
    this.state.players.set(client.sessionId, new Player());
  }

  onLeave (client: Client, consented: boolean) {
    console.log(client.sessionId, "left!");
    this.state.players.delete(client.sessionId);
  }

  onDispose() {
    console.log("room", this.roomId, "disposing...");
  }

}
