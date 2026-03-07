export declare const generators: Record<string, any>;
export interface GenerateOptions {
    files: string[];
    output: string;
    decorator?: string;
    namespace?: string;
    bundle?: boolean;
}
export declare function generate(targetId: string, options: GenerateOptions): void;
