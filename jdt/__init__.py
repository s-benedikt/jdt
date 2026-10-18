"""JDT - JSON Document Type Schema Language Parser & Validator.

A Python library for parsing JDT schemas and validating JSON documents.
"""

from typing import Any, List, Tuple, Union
import json

from .lexer import Lexer, TokenType, Token
from .parser import (
    Parser,
    Validator,
    Schema,
    PropertyDef,
    Constraint,
    parse_and_validate,
)

__version__ = "0.1.0"


def compile(schema_source: str) -> Validator:
    """Parse a JDT schema string and return a reusable Validator object."""
    parser = Parser(schema_source)
    schema = parser.parse()
    return Validator(schema)


def validate(
    schema: Union[str, Schema, Validator],
    data: Any
) -> Tuple[bool, List[str]]:
    """Validate data against a JDT schema.

    Args:
        schema: A JDT schema string, a parsed Schema object, or a Validator object.
        data: A Python dict/list/primitive or a JSON string.

    Returns:
        A tuple of `(is_valid, error_list)`.
    """
    if isinstance(schema, str):
        validator = compile(schema)
    elif isinstance(schema, Schema):
        validator = Validator(schema)
    elif isinstance(schema, Validator):
        validator = schema
    else:
        raise TypeError(f"Expected schema string, Schema, or Validator, got {type(schema).__name__}")

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            pass

    return validator.validate(data)


__all__ = [
    "Parser",
    "Validator",
    "Schema",
    "PropertyDef",
    "Constraint",
    "Lexer",
    "TokenType",
    "Token",
    "parse_and_validate",
    "compile",
    "validate",
    "__version__",
]
