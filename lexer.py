"""Backward-compatibility shim for lexer.

Recommended usage:
    from jdt import Lexer, TokenType, Token
"""

from jdt.lexer import *
from jdt.lexer import (
    Lexer,
    TokenType,
    Token,
)

__all__ = [
    "Lexer",
    "TokenType",
    "Token",
]
