import { OPERATION } from "../encoding/spec.js";
import { Schema } from "../Schema.js";
import type { IRef, Ref } from "../encoder/ChangeTree.js";
import type { Decoder } from "./Decoder.js";
import { Iterator } from "../encoding/decode.js";
export interface DataChange<T = any, F = string> {
    ref: IRef;
    refId: number;
    op: OPERATION;
    field: F;
    dynamicIndex?: number | string;
    value: T;
    previousValue: T;
}
export declare const DEFINITION_MISMATCH = -1;
export type DecodeOperation<T extends Schema = any> = (decoder: Decoder<T>, bytes: Uint8Array, it: Iterator, ref: IRef, allChanges: DataChange[]) => number | void;
export declare function decodeValue<T extends Ref>(decoder: Decoder, operation: OPERATION, ref: T, index: number, type: any, bytes: Uint8Array, it: Iterator, allChanges: DataChange[]): {
    value: any;
    previousValue: T;
};
export declare const decodeSchemaOperation: DecodeOperation;
export declare const decodeKeyValueOperation: DecodeOperation;
export declare const decodeArray: DecodeOperation;
