# JDT

This repository contains a parser and validator for the JSON Document Type (JDT) schema language, along with several accessories.

It contains the following files and folders:
- `parser.py`: The main parser and validator implementation.
- `lexer.py`: The lexer for tokenizing the JDT schema.
- `test_parser.py`: A set of test cases to validate the functionality of the parser and validator.
- `jdt-auto-complete/`: Directory containing code for auto-completion in VS Code. 
    - `/src/extension.ts`: Main file for the VS Code extension.
    - `/syntaxes/jdt.tmLanguage.json`: Syntax highlighting for JDT.
- `.github/`: Directory containing GitHub Copilot instructions.
- `jdt.md` and `jdt.pdf`: Specification of the JDT schema language.
- `grammar.ebnf`: JDT EBNF grammar.
- `visualization.py`: Creates a visualization of the AST using `visualize_ast.py`.
- `requirements.txt`: Python dependencies for the project.
- `app.py`: Web interface for JDT.

To execute, go to `app.py` and run the script. You will need to create a virtual Python environment and install the dependencies listed in `requirements.txt`.

You can then launch the web interface in your browser at `http://127.0.0.1:5000` or go to `https://jdt.fids.ur.de` to use the hosted version.

To use the VS Code extension, you need Visual Studio Code. Open the `extension.ts` file and, in the menu bar, click `Run` > `Start Debugging`. A new window will open with the extension enabled. All `*.jdt` files will be highlighted and auto-completion will be available. GitHub Copilot will work depending on your settings and subscription. In the bottom-right corner, you can click the Copilot icon to enable or disable Copilot. In the future, the extension will be available in the VS Code Marketplace.

The following is a short description of the functionality of the lexer and parser.


Lexer functionality:
- Tokenizes JDT schema text into a sequence of tokens.
- Handles keys, constraints, and indentation according to the JDT specification.
- Provides error handling for invalid tokens.

Parser functionality:
- Parses the token sequence from the lexer into an internal representation of the JDT schema (an Abstract Syntax Tree).
- Validates JSON documents against the parsed schema.
- Provides detailed error messages for validation failures.

For the definition of the JDT Schema Language, refer to the `jdt.md` file.