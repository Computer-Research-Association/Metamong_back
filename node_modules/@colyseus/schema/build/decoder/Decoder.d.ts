import { TypeContext } from "../types/TypeContext.js";
import { Schema } from "../Schema.js";
import type { IRef } from "../encoder/ChangeTree.js";
import type { Iterator } from "../encoding/decode.js";
import { ReferenceTracker } from "./ReferenceTracker.js";
import { type DataChange } from "./DecodeOperation.js";
import { Collection } from "../types/HelperTypes.js";
export declare class Decoder<T extends IRef = any> {
    context: TypeContext;
    state: T;
    root: ReferenceTracker;
    currentRefId: number;
    triggerChanges?: (allChanges: DataChange[]) => void;
    constructor(root: T, context?: TypeContext);
    protected setState(root: T): void;
    decode(bytes: Uint8Array, it?: Iterator, ref?: IRef): DataChange<any, string>[];
    skipCurrentStructure(bytes: Uint8Array, it: Iterator, totalBytes: number): void;
    getInstanceType(bytes: Uint8Array, it: Iterator, defaultType: typeof Schema): typeof Schema;
    createInstanceOfType(type: typeof Schema): Schema;
    removeChildRefs(ref: Collection, allChanges: DataChange[]): void;
}
