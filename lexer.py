"""Lexer for JDT schema language."""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator, Any


class TokenType(Enum):
    """Token types in JDT schema."""
    # Literals
    NAME = auto()
    NUMBER = auto()
    STRING = auto()
    REGEX = auto()
    
    # Keywords
    IS = auto()
    DEFINED = auto()
    REQUIRED = auto()
    OPTIONAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    ARRAY = auto()
    CLOSED = auto()
    OPEN = auto()
    MATCH = auto()
    MINIMUM = auto()
    MAXIMUM = auto()
    LONGER = auto()
    SHORTER = auto()
    LARGER = auto()
    SMALLER = auto()
    SCHEMA = auto()
    VERSION = auto()
    OWNER = auto()
    TYPE = auto()
    
    # Primitives
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    STRING_TYPE = auto()
    NUMBER_TYPE = auto()
    BOOLEAN_TYPE = auto()
    OBJECT_TYPE = auto()
    
    # Operators
    LPAREN = auto()
    RPAREN = auto()
    COLON = auto()
    
    # Meta
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    """A single token."""
    type: TokenType
    value: Any
    line: int
    col: int


class Lexer:
    """Tokenize JDT schema language."""
    
    KEYWORDS = {
        'is': TokenType.IS,
        'defined': TokenType.DEFINED,
        'required': TokenType.REQUIRED,
        'optional': TokenType.OPTIONAL,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'array': TokenType.ARRAY,
        'closed': TokenType.CLOSED,
        'open': TokenType.OPEN,
        'match': TokenType.MATCH,
        'minimum': TokenType.MINIMUM,
        'maximum': TokenType.MAXIMUM,
        'longer': TokenType.LONGER,
        'shorter': TokenType.SHORTER,
        'larger': TokenType.LARGER,
        'smaller': TokenType.SMALLER,
        'schema': TokenType.SCHEMA,
        'version': TokenType.VERSION,
        'owner': TokenType.OWNER,
        'type': TokenType.TYPE,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'null': TokenType.NULL,
        'string': TokenType.STRING_TYPE,
        'number': TokenType.NUMBER_TYPE,
        'boolean': TokenType.BOOLEAN_TYPE,
        'object': TokenType.OBJECT_TYPE,
    }
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.indent_stack = [0]
        self.at_line_start = True
        self.pending_dedents = 0
    
    def error(self, msg: str):
        raise SyntaxError(f"Lexer error at line {self.line}, col {self.col}: {msg}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character without consuming."""
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """Consume and return next character."""
        if self.pos < len(self.text):
            ch = self.text[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            return ch
        return None
    
    def skip_whitespace_inline(self) -> int:
        """Skip spaces/tabs, return count."""
        count = 0
        while self.peek() in (' ', '\t'):
            self.advance()
            count += 1
        return count
    
    def handle_indent(self) -> Iterator[Token]:
        """Handle indentation at start of line."""
        if not self.at_line_start:
            return
        
        self.at_line_start = False
        indent_level = 0
        
        while self.peek() in (' ', '\t'):
            if self.peek() == '\t':
                indent_level += 4
            else:
                indent_level += 1
            self.advance()
        
        # Skip empty lines and comments
        if self.peek() in ('\n', None) or (self.peek() == '"' and self.peek(1) == '"' and self.peek(2) == '"'):
            return
        
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            yield Token(TokenType.INDENT, None, self.line, self.col)
        elif indent_level < current_indent:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                yield Token(TokenType.DEDENT, None, self.line, self.col)
            if self.indent_stack[-1] != indent_level:
                self.error(f"Inconsistent indentation")
    
    def read_string(self, quote_char: str) -> str:
        """Read a quoted string."""
        result = ""
        self.advance()  # Skip opening quote
        
        while True:
            ch = self.peek()
            if ch is None:
                self.error("Unterminated string")
            if ch == quote_char:
                self.advance()
                break
            if ch == '\\':
                self.advance()
                next_ch = self.advance()
                if next_ch == 'n':
                    result += '\n'
                elif next_ch == 't':
                    result += '\t'
                elif next_ch == '\\':
                    result += '\\'
                elif next_ch == quote_char:
                    result += quote_char
                else:
                    if next_ch is None:
                        self.error("Unterminated string")
                    result += next_ch
            else:
                result += ch
                self.advance()
        
        return result
    
    def read_comment(self) -> str:
        """Read a triple-quote comment block."""
        self.advance()
        self.advance()
        self.advance()
        result = ""
        
        while True:
            if self.peek() is None:
                self.error("Unterminated comment")
            if self.peek() == '"' and self.peek(1) == '"' and self.peek(2) == '"':
                self.advance()
                self.advance()
                self.advance()
                break
            result += self.advance() # type: ignore
        
        return result
    
    def read_number(self) -> float:
        """Read a number (int or float)."""
        result = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'): # type: ignore
            result += self.advance() # type: ignore
        
        if '.' in result:
            return float(result)
        return int(result)
    
    def read_name(self) -> str:
        """Read a name/identifier, supporting quoted sections."""
        result = ""
        
        while self.peek():
            ch = self.peek()
            # Stop at triple quotes (comment)
            if ch == '"' and self.peek(1) == '"' and self.peek(2) == '"':
                break
            # Handle quoted sections within names
            if ch == '"':
                result += self.advance()  # type: ignore # Add opening quote
                while True:
                    ch = self.peek()
                    if ch is None:
                        self.error("Unterminated quoted section in name")
                    if ch == '"' and not (self.peek(1) == '"' and self.peek(2) == '"'):
                        result += self.advance()  # type: ignore # Add closing quote
                        break
                    result += self.advance() # type: ignore
            # Stop at delimiters
            elif ch in (' ', '\n', '\t', ':', '(', ')', ','):
                break
            else:
                result += self.advance() # type: ignore
        
        return result
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire input."""
        tokens = []
        
        while self.pos < len(self.text):
            # Handle indentation at line start
            if self.at_line_start:
                for token in self.handle_indent():
                    tokens.append(token)
            
            ch = self.peek()
            
            if ch is None:
                break
            
            if ch == '\n':
                self.advance()
                self.at_line_start = True
                tokens.append(Token(TokenType.NEWLINE, None, self.line - 1, self.col))
                continue
            
            if ch in (' ', '\t'):
                self.advance()
                continue
            
            # Comment or regex
            if ch == '"' and self.peek(1) == '"' and self.peek(2) == '"':
                content = self.read_comment()
                last_token = tokens[-1] if tokens else None
                # If last token is LPAREN and token before that is MATCH, it's a regex
                if (last_token and last_token.type == TokenType.LPAREN and 
                    len(tokens) > 1 and tokens[-2].type == TokenType.MATCH):
                    tokens.append(Token(TokenType.REGEX, content, self.line, self.col))
                else:
                    tokens.append(Token(TokenType.COMMENT, content, self.line, self.col))
                continue
            
            # String literal
            if ch == '"':
                string_val = self.read_string('"')
                tokens.append(Token(TokenType.STRING, string_val, self.line, self.col))
                continue
            
            # Number
            if ch.isdigit():
                num = self.read_number()
                tokens.append(Token(TokenType.NUMBER, num, self.line, self.col))
                continue
            
            # Regex
            if ch == '(':
                # Look ahead for regex pattern
                next_ch = self.peek(1)
                if next_ch is not None and not next_ch.isspace():
                    # Could be match(regex), handled by parser
                    pass
                tokens.append(Token(TokenType.LPAREN, None, self.line, self.col))
                self.advance()
                continue
            
            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, None, self.line, self.col))
                self.advance()
                continue
            
            if ch == ':':
                tokens.append(Token(TokenType.COLON, None, self.line, self.col))
                self.advance()
                continue

            if ch == ',':
                tokens.append(Token(TokenType.AND, None, self.line, self.col))
                self.advance()
                continue
            
            # Name/keyword
            name = self.read_name()
            if name:
                token_type = self.KEYWORDS.get(name, TokenType.NAME)
                tokens.append(Token(token_type, name, self.line, self.col))
            else:
                self.error(f"Unexpected character: {ch}")
        
        # Handle remaining dedents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, None, self.line, self.col))
        
        tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return tokens
