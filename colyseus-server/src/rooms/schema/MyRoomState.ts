import { Schema, type, MapSchema } from "@colyseus/schema";

export class Player extends Schema {
  @type("number") x: number = 0;
  @type("number") y: number = 0;
  @type("number") speed: number = 5; // Default speed

  // Input state (not synchronized)
  inputX: number = 0;
  inputY: number = 0;
}

export class MyRoomState extends Schema {

  @type({ map: Player }) players = new MapSchema<Player>();

}
