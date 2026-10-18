"""Backward-compatibility shim for parser.

Recommended usage:
    from jdt import Parser, Validator, Schema, PropertyDef, Constraint, parse_and_validate
"""

from jdt.parser import *
from jdt.parser import (
    Parser,
    Validator,
    Schema,
    PropertyDef,
    Constraint,
    parse_and_validate,
)

__all__ = [
    "Parser",
    "Validator",
    "Schema",
    "PropertyDef",
    "Constraint",
    "parse_and_validate",
]
