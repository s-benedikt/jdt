"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
function activate(context) {
    const jdtProvider = vscode.languages.registerCompletionItemProvider({ scheme: 'file', language: 'jdt' }, {
        provideCompletionItems(document, position) {
            const completions = [];
            // --- 1. Root Parameters ---
            const rootParams = ['schema', 'version', 'owner', 'type'];
            rootParams.forEach(param => {
                const item = new vscode.CompletionItem(param, vscode.CompletionItemKind.Property);
                item.detail = "JDT Root Parameter";
                completions.push(item);
            });
            // --- 2. Primitives & Simple Constraints ---
            const primitives = ['string', 'number', 'boolean', 'null', 'true', 'false'];
            primitives.forEach(prim => {
                const item = new vscode.CompletionItem(prim, vscode.CompletionItemKind.TypeParameter);
                item.detail = "JDT Primitive / Simple Constraint";
                completions.push(item);
            });
            // --- 3. Occurrence Constraints ---
            const occurrences = ['required', 'optional'];
            occurrences.forEach(occ => {
                const item = new vscode.CompletionItem(occ, vscode.CompletionItemKind.Keyword);
                item.detail = "JDT Occurrence Constraint";
                item.documentation = occ === 'optional' ? "Default occurrence if not specified." : "Exactly one occurrence.";
                completions.push(item);
            });
            // --- 4. Operator Constraints ---
            const operators = ['and', 'or', 'not'];
            operators.forEach(op => {
                const item = new vscode.CompletionItem(op, vscode.CompletionItemKind.Operator);
                item.detail = "JDT Operator Constraint";
                completions.push(item);
            });
            // --- 5. Value and Length Constraints ---
            const valueConstraints = ['minimum', 'maximum', 'longer', 'shorter', 'larger', 'smaller'];
            valueConstraints.forEach(vc => {
                const item = new vscode.CompletionItem(vc, vscode.CompletionItemKind.Keyword);
                item.detail = "JDT Value/Length Constraint";
                completions.push(item);
            });
            // --- 6. Undefined Constraints ---
            const undefinedConstraints = ['closed', 'open', 'unordered', 'ordered'];
            undefinedConstraints.forEach(uc => {
                const item = new vscode.CompletionItem(uc, vscode.CompletionItemKind.Keyword);
                item.detail = "JDT Undefined Constraint";
                completions.push(item);
            });
            // --- 7. Snippets for Complex Data Types & Regex ---
            // Array Snippet
            const arraySnippet = new vscode.CompletionItem('array', vscode.CompletionItemKind.Snippet);
            arraySnippet.insertText = new vscode.SnippetString('array(${1:datatype})');
            arraySnippet.detail = "JDT Array Constraint";
            completions.push(arraySnippet);
            // Defined Data Type Snippet
            const definedSnippet = new vscode.CompletionItem('defined', vscode.CompletionItemKind.Snippet);
            definedSnippet.insertText = new vscode.SnippetString('defined ${1:TypeName}:\n\t$0');
            definedSnippet.detail = "JDT Custom Data Type";
            completions.push(definedSnippet);
            // Regex Match Snippet
            const matchSnippet = new vscode.CompletionItem('match', vscode.CompletionItemKind.Snippet);
            matchSnippet.insertText = new vscode.SnippetString('match("""${1:regex}""")');
            matchSnippet.detail = "JDT Regex Constraint";
            completions.push(matchSnippet);
            // Comment Snippet
            const commentSnippet = new vscode.CompletionItem('comment', vscode.CompletionItemKind.Snippet);
            commentSnippet.insertText = new vscode.SnippetString('""" ${1:Comment} """');
            commentSnippet.detail = "JDT Block Comment";
            completions.push(commentSnippet);
            // The 'is' keyword
            const isKeyword = new vscode.CompletionItem('is', vscode.CompletionItemKind.Keyword);
            isKeyword.detail = "JDT Constraint Keyword";
            completions.push(isKeyword);
            return completions;
        }
    }, ' ', // Trigger completion on space (useful after typing 'is ')
    'i' // Trigger completion when typing 'i' (for 'is')
    );
    context.subscriptions.push(jdtProvider);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map