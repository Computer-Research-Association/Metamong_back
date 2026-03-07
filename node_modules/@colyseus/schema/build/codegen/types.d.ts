export declare function getCommentHeader(singleLineComment?: string): string;
export declare class Context {
    classes: Class[];
    interfaces: Interface[];
    enums: Enum[];
    getStructures(): {
        classes: Class[];
        interfaces: Interface[];
        enums: Enum[];
    };
    addStructure(structure: IStructure): void;
    private getParentClass;
    private isSchemaClass;
}
export interface IStructure {
    context: Context;
    name: string;
    properties: Property[];
    addProperty(property: Property): void;
}
export declare class Interface implements IStructure {
    context: Context;
    name: string;
    properties: Property[];
    addProperty(property: Property): void;
}
export declare class Class implements IStructure {
    context: Context;
    name: string;
    properties: Property[];
    extends: string;
    addProperty(property: Property): void;
    postProcessing(): void;
}
export declare class Enum implements IStructure {
    context: Context;
    name: string;
    properties: Property[];
    addProperty(property: Property): void;
}
export declare class Property {
    index: number;
    name: string;
    type: string;
    childType: string;
    deprecated?: boolean;
}
export interface File {
    name: string;
    content: string;
}
/**
 * Structured file representation for code generation.
 * Separates imports, local references, and body content to enable
 * clean bundling without string parsing.
 */
export interface GeneratedFile {
    name: string;
    /** External imports (e.g., "@colyseus/schema", "Colyseus.Schema") */
    imports: string[];
    /** References to other generated classes (used for imports in non-bundle mode) */
    localRefs: string[];
    /** The class/interface/enum definition body (without imports or namespace wrapper) */
    body: string;
}
export declare function getInheritanceTree(klass: Class, allClasses: Class[], includeSelf?: boolean): Class[];
