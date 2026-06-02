# JDT

This repository contains a parser and validator for the JSON Document Type (JDT) Schema Language and several accessories.

It contains the following files and folders:
- `parser.py`: The main parser and validator implementation.
- `lexer.py`: The lexer for tokenizing the JDT schema.
- `test_parser.py`: A set of test cases to validate the functionality of the parser and validator.
- `jdt-auto-complete/`: Directory containing code for auto-completion in VSCode.
- `.github/`: Directory containing GitHub Copilot instructions.

To test the parser and validator, use the test cases defined in `test_parser.py`. An interface will be added in the future.

Lexer functionality:
- Tokenizes JDT schema text into a sequence of tokens.
- Handles comments, names, and various symbols according to the JDT specification.
- Provides error handling for invalid tokens.

Parser functionality:
- Parses the token sequence from the lexer into an internal representation of the JDT schema.
- Validates JSON documents against the parsed schema.
- Provides detailed error messages for validation failures.

For the definition of the JDT Schema Language, refer to the `jdt.md` file.