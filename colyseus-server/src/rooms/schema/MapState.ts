import { Schema, type } from "@colyseus/schema";

class MapState extends Schema {
    @type("int32") width: number = 0;
    @type("int32") height: number = 0;
}
