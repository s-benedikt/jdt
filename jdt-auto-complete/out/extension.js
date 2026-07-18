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
    // Track defined types across the document
    const extractDefinedTypes = (document) => {
        const types = [];
        const text = document.getText();
        const definedRegex = /define\s+(\w+)/g;
        let match;
        while ((match = definedRegex.exec(text)) !== null) {
            const pos = document.positionAt(match.index);
            types.push({ name: match[1], line: pos.line });
        }
        return types;
    };
    // Determine context using multi-line indentation analysis
    const getContext = (document, position) => {
        const line = document.lineAt(position.line).text;
        const beforeCursor = line.substring(0, position.character);
        // 1. Are we typing a constraint on the current line?
        if (/\bis\b/.test(beforeCursor)) {
            if (/\b(and|or)\s*$/.test(beforeCursor)) {
                return 'after-operator';
            }
            if (/,\s*$/.test(beforeCursor)) {
                return 'after-comma';
            }
            if (/\bis\s*$/.test(beforeCursor)) {
                return 'after-is';
            }
            if (/\(\s*$/.test(beforeCursor)) {
                return 'after-paren';
            }
            return 'in-constraint-value';
        }
        // 2. Start of line or typing a keyword/name at start of line
        if (/^\s*[a-zA-Z]*$/.test(beforeCursor)) {
            const currentIndent = beforeCursor.match(/^\s*/)?.[0].length || 0;
            if (currentIndent === 0) {
                return 'root-start';
            }
            else {
                return 'container-start';
            }
        }
        // 3. After a name (e.g. "name ", "name i") - ready for "is"
        if (/^\s*[^\s:]+\s+[a-zA-Z]*$/.test(beforeCursor)) {
            if (/^\s*define\s/.test(beforeCursor)) {
                return 'after-define';
            }
            return 'after-name';
        }
        return 'none';
    };
    const jdtProvider = vscode.languages.registerCompletionItemProvider({ scheme: 'file', language: 'jdt' }, {
        provideCompletionItems(document, position) {
            const completions = [];
            const context = getContext(document, position);
            const definedTypes = extractDefinedTypes(document);
            const currentIndent = document.lineAt(position.line).text.match(/^\s*/)?.[0].length || 0;
            const isConstraintContext = ['after-is', 'after-comma', 'after-operator', 'after-paren', 'in-constraint-value'].includes(context);
            // After 'is' keyword - suggest constraint types
            if (isConstraintContext) {
                // Simple type constraints
                ['string', 'number', 'boolean', 'null', 'true', 'false'].forEach(type => {
                    const item = new vscode.CompletionItem(type, vscode.CompletionItemKind.TypeParameter);
                    item.detail = 'JDT Simple Type';
                    item.sortText = '1';
                    completions.push(item);
                });
                // Defined types (if available)
                definedTypes.forEach(dt => {
                    const item = new vscode.CompletionItem(dt.name, vscode.CompletionItemKind.Class);
                    item.detail = `Custom data type (defined on line ${dt.line + 1})`;
                    item.sortText = '1';
                    completions.push(item);
                });
                if (currentIndent === 0) {
                    const rootParams = [
                        { label: 'schema', detail: 'URI for parent schema' },
                        { label: 'version', detail: 'Version URI' },
                        { label: 'owner', detail: "Owner's URL" },
                        { label: 'type', detail: 'Root object type' }
                    ];
                    rootParams.forEach(param => {
                        const item = new vscode.CompletionItem(param.label, vscode.CompletionItemKind.Property);
                        item.detail = `JDT Root Parameter: ${param.detail}`;
                        item.sortText = '1_root';
                        completions.push(item);
                    });
                }
                // Array constraint
                const arraySnippet = new vscode.CompletionItem('array', vscode.CompletionItemKind.Snippet);
                arraySnippet.insertText = new vscode.SnippetString('array(${1:datatype})');
                arraySnippet.detail = 'Array constraint with optional datatype';
                arraySnippet.sortText = '2';
                completions.push(arraySnippet);
                // Regex match - corrected format (uses triple quotes)
                const matchSnippet = new vscode.CompletionItem('match', vscode.CompletionItemKind.Snippet);
                matchSnippet.insertText = new vscode.SnippetString('match("""${1:regex}""")');
                matchSnippet.detail = 'Regex constraint for pattern matching';
                matchSnippet.sortText = '2';
                completions.push(matchSnippet);
                // Occurrence constraints
                ['required', 'optional'].forEach(occ => {
                    const item = new vscode.CompletionItem(occ, vscode.CompletionItemKind.Keyword);
                    item.detail = `Occurrence: ${occ === 'optional' ? 'Zero or one' : 'Exactly one'}`;
                    item.sortText = '3';
                    completions.push(item);
                });
                // Operator constraints
                if (context === 'in-constraint-value') {
                    ['and', 'or'].forEach(op => {
                        const item = new vscode.CompletionItem(op, vscode.CompletionItemKind.Operator);
                        item.detail = 'JDT Operator';
                        item.sortText = '0_op'; // High priority when chaining
                        completions.push(item);
                    });
                }
                else {
                    const item = new vscode.CompletionItem('not', vscode.CompletionItemKind.Operator);
                    item.detail = 'JDT Operator';
                    item.sortText = '0_op';
                    completions.push(item);
                }
                // Value/length constraints
                ['minimum', 'maximum', 'longer', 'shorter', 'larger', 'smaller'].forEach(vc => {
                    const item = new vscode.CompletionItem(vc, vscode.CompletionItemKind.Keyword);
                    item.detail = 'Value/Length constraint (requires number after)';
                    item.sortText = '4';
                    completions.push(item);
                });
                // Undefined constraints
                ['closed', 'open', 'unordered', 'ordered'].forEach(uc => {
                    const item = new vscode.CompletionItem(uc, vscode.CompletionItemKind.Keyword);
                    item.detail = 'Undefined key constraint';
                    item.sortText = '5';
                    completions.push(item);
                });
                // Parentheses for complex expressions
                const parenSnippet = new vscode.CompletionItem('()', vscode.CompletionItemKind.Snippet);
                parenSnippet.insertText = new vscode.SnippetString('(${1:constraint})');
                parenSnippet.detail = 'Group constraints';
                parenSnippet.sortText = '6';
                completions.push(parenSnippet);
                return completions;
            }
            if (context === 'root-start') {
                const isKeyword = new vscode.CompletionItem('is', vscode.CompletionItemKind.Keyword);
                isKeyword.detail = 'JDT constraint keyword';
                completions.push(isKeyword);
                const definedSnippet = new vscode.CompletionItem('define', vscode.CompletionItemKind.Snippet);
                definedSnippet.insertText = new vscode.SnippetString('define ${1:TypeName}:\n\t${2:field is type}');
                definedSnippet.detail = 'Define custom data type';
                completions.push(definedSnippet);
                const commentSnippet = new vscode.CompletionItem('"""', vscode.CompletionItemKind.Snippet);
                commentSnippet.insertText = new vscode.SnippetString('""" ${1:comment} """');
                commentSnippet.detail = 'Block comment';
                completions.push(commentSnippet);
                return completions;
            }
            if (context === 'container-start' || context === 'after-name') {
                const isKeyword = new vscode.CompletionItem('is', vscode.CompletionItemKind.Keyword);
                isKeyword.detail = 'JDT constraint keyword';
                completions.push(isKeyword);
                const commentSnippet = new vscode.CompletionItem('"""', vscode.CompletionItemKind.Snippet);
                commentSnippet.insertText = new vscode.SnippetString('""" ${1:comment} """');
                commentSnippet.detail = 'Block comment';
                completions.push(commentSnippet);
                return completions;
            }
            return completions;
        }
    }, ' ', 'i', 'a', 'o', 'n', 'm', '(', ':', 'd');
    // Diagnostics provider for basic validation
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('jdt');
    const validateDocument = (document) => {
        if (document.languageId !== 'jdt')
            return;
        const diagnostics = [];
        const text = document.getText();
        // Check for invalid 'is' usage (bare 'is' as name, not escaped)
        const lines = document.getText().split('\n');
        lines.forEach((line, idx) => {
            const bareIsMatch = line.match(/^\s*is\s*$/);
            if (bareIsMatch) {
                diagnostics.push(new vscode.Diagnostic(new vscode.Range(idx, 0, idx, line.length), "Bare 'is' is not allowed as a name. Use escape like #is or \\is", vscode.DiagnosticSeverity.Error));
            }
            // Check for unclosed triple quotes
            const quoteMatches = (line.match(/"""/g) || []).length;
            if (quoteMatches % 2 !== 0) {
                diagnostics.push(new vscode.Diagnostic(new vscode.Range(idx, 0, idx, line.length), 'Unclosed triple-quote string', vscode.DiagnosticSeverity.Warning));
            }
        });
        diagnosticCollection.set(document.uri, diagnostics);
    };
    const docChangeSubscription = vscode.workspace.onDidChangeTextDocument(event => {
        validateDocument(event.document);
    });
    context.subscriptions.push(jdtProvider, diagnosticCollection, docChangeSubscription);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map