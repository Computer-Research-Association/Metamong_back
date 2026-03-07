import { OPERATION } from "../encoding/spec.js";
import type { ChangeTree, Ref } from "./ChangeTree.js";
import type { Encoder } from "./Encoder.js";
import type { Iterator } from "../encoding/decode.js";
import type { Metadata } from "../Metadata.js";
export type EncodeOperation<T extends Ref = any> = (encoder: Encoder, bytes: Uint8Array, changeTree: ChangeTree<T>, index: number, operation: OPERATION, it: Iterator, isEncodeAll: boolean, hasView: boolean, metadata?: Metadata) => void;
export declare function encodeValue(encoder: Encoder, bytes: Uint8Array, type: any, value: any, operation: OPERATION, it: Iterator): void;
/**
 * Used for Schema instances.
 * @private
 */
export declare const encodeSchemaOperation: EncodeOperation;
/**
 * Used for collections (MapSchema, CollectionSchema, SetSchema)
 * @private
 */
export declare const encodeKeyValueOperation: EncodeOperation;
/**
 * Used for collections (MapSchema, ArraySchema, etc.)
 * @private
 */
export declare const encodeArray: EncodeOperation;
