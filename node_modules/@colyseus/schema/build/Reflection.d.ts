import { schema, SchemaType } from "./annotations.js";
import { Iterator } from "./encoding/decode.js";
import { Encoder } from "./encoder/Encoder.js";
import { Decoder } from "./decoder/Decoder.js";
import { Schema } from "./Schema.js";
/**
 * Static methods available on Reflection
 */
interface ReflectionStatic {
    /**
     * Encodes the TypeContext of an Encoder into a buffer.
     *
     * @param encoder Encoder instance
     * @param it
     * @returns
     */
    encode: (encoder: Encoder, it?: Iterator) => Uint8Array;
    /**
     * Decodes the TypeContext from a buffer into a Decoder instance.
     *
     * @param bytes Reflection.encode() output
     * @param it
     * @returns Decoder instance
     */
    decode: <T extends Schema = Schema>(bytes: Uint8Array, it?: Iterator) => Decoder<T>;
}
/**
 * Reflection
 */
export declare const ReflectionField: import("./annotations.js").SchemaWithExtendsConstructor<{
    name: "string";
    type: "string";
    referencedType: "number";
}, import("./index.js").AssignableProps<import("./index.js").InferSchemaInstanceType<{
    name: "string";
    type: "string";
    referencedType: "number";
}>>, typeof Schema>;
export type ReflectionField = SchemaType<typeof ReflectionField>;
export declare const ReflectionType: import("./annotations.js").SchemaWithExtendsConstructor<{
    id: "number";
    extendsId: "number";
    fields: import("./annotations.js").SchemaWithExtendsConstructor<{
        name: "string";
        type: "string";
        referencedType: "number";
    }, import("./index.js").AssignableProps<import("./index.js").InferSchemaInstanceType<{
        name: "string";
        type: "string";
        referencedType: "number";
    }>>, typeof Schema>[];
}, import("./index.js").AssignableProps<import("./index.js").InferSchemaInstanceType<{
    id: "number";
    extendsId: "number";
    fields: import("./annotations.js").SchemaWithExtendsConstructor<{
        name: "string";
        type: "string";
        referencedType: "number";
    }, import("./index.js").AssignableProps<import("./index.js").InferSchemaInstanceType<{
        name: "string";
        type: "string";
        referencedType: "number";
    }>>, typeof Schema>[];
}>>, typeof Schema>;
export type ReflectionType = SchemaType<typeof ReflectionType>;
export declare const Reflection: ReturnType<typeof schema<{
    types: [typeof ReflectionType];
    rootType: "number";
}>> & ReflectionStatic;
export type Reflection = SchemaType<typeof Reflection>;
export {};
