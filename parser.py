"""JDT Schema Parser and JSON Validator."""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from lexer import Lexer, TokenType, Token


@dataclass
class Constraint:
    """Represents a constraint on a property."""
    type: str
    value: Any = None
    children: List['Constraint'] = field(default_factory=list)


@dataclass
class PropertyDef:
    """Definition of a property."""
    name: str
    constraint: Optional[Constraint] = None
    closed: bool = False
    ordered: bool = False
    is_container: bool = False
    children: Dict[str, 'PropertyDef'] = field(default_factory=dict)


@dataclass
class Schema:
    """Parsed JDT schema."""
    root_type: str = "object"
    schema_uri: Optional[str] = None
    version_uri: Optional[str] = None
    owner_uri: Optional[str] = None
    closed: bool = False
    ordered: bool = False
    properties: Dict[str, PropertyDef] = field(default_factory=dict)
    custom_types: Dict[str, PropertyDef] = field(default_factory=dict)


class Parser:
    """Parse JDT schema and validate JSON."""
    
    def __init__(self, schema_text: str):
        self.schema_text = schema_text
        lexer = Lexer(schema_text)
        self.tokens = lexer.tokenize()
        self.pos = 0
        self.schema = Schema()
    
    def error(self, msg: str):
        token = self.current_token()
        raise SyntaxError(f"Parse error at line {token.line}: {msg}")
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]
    
    def peek_token(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self) -> Token:
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type."""
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type}, got {token.type}")
        return self.advance()
    
    def skip_trivia(self):
        """Skip newlines and comments"""
        while self.current_token().type in (TokenType.NEWLINE, TokenType.COMMENT):
            self.advance()
    
    def parse(self) -> Schema:
        self.skip_trivia()
        
        # Parse root declarations and custom types
        while self.current_token().type == TokenType.IS:
            self.advance()
            
            # Check if this is a custom type definition
            if self.current_token().type == TokenType.DEFINED:
                self.parse_defined_type()
            else:
                self.parse_root_declaration()
            
            self.skip_trivia()
        
        # Parse properties
        self.parse_properties(self.schema.properties)
        
        return self.schema
    
    def parse_root_declaration(self):
        """Parse root declaration (schema, version, owner, type)."""
        token = self.current_token()
        
        if token.type == TokenType.SCHEMA:
            self.advance()
            uri = self.expect(TokenType.STRING).value
            self.schema.schema_uri = uri
        elif token.type == TokenType.VERSION:
            self.advance()
            uri = self.expect(TokenType.STRING).value
            self.schema.version_uri = uri
        elif token.type == TokenType.OWNER:
            self.advance()
            uri = self.expect(TokenType.STRING).value
            self.schema.owner_uri = uri
        elif token.type == TokenType.TYPE:
            self.advance()
            type_token = self.current_token()
            if type_token.type in (TokenType.OBJECT_TYPE, TokenType.ARRAY):
                self.schema.root_type = type_token.value
                self.advance()
            else:
                self.error(f"Expected type, got {type_token.type}")
        elif token.type in (TokenType.CLOSED, TokenType.ORDERED, TokenType.OPEN, TokenType.UNORDERED):
            self.parse_global_constraints()
    
    def parse_global_constraints(self):
        """Parse global constraints like closed, ordered."""
        while True:
            token = self.current_token()
            if token.type == TokenType.CLOSED:
                self.schema.closed = True
                self.advance()
            elif token.type == TokenType.ORDERED:
                self.schema.ordered = True
                self.advance()
            elif token.type == TokenType.OPEN:
                self.schema.closed = False
                self.advance()
            elif token.type == TokenType.UNORDERED:
                self.schema.ordered = False
                self.advance()
            elif token.type == TokenType.AND:
                self.advance()
            else:
                break
            self.skip_trivia()
    
    def parse_defined_type(self):
        """Parse a defined custom type."""
        self.expect(TokenType.DEFINED)
        name_token = self.expect(TokenType.NAME)
        name = name_token.value
        
        self.expect(TokenType.COLON)
        self.skip_trivia()
        
        prop_def = PropertyDef(name=name, is_container=True)
        
        if self.current_token().type == TokenType.INDENT:
            self.advance()
            self.parse_properties(prop_def.children, expect_dedent=True)
        
        self.schema.custom_types[name] = prop_def
    
    def parse_properties(self, target_dict: Dict[str, PropertyDef], expect_dedent: bool = False):
        """Parse property definitions at current indentation level."""
        while True:
            self.skip_trivia()
            
            token = self.current_token()
            
            if token.type == TokenType.DEDENT:
                if expect_dedent:
                    self.advance()
                break
            elif token.type in (TokenType.EOF,):
                break
            
            if token.type != TokenType.NAME:
                break
            
            name = token.value
            self.advance()
            
            is_container = self.current_token().type == TokenType.COLON
            
            if is_container:
                self.advance()
                self.skip_trivia()
                prop_def = PropertyDef(name=name, is_container=True)
                
                if self.current_token().type == TokenType.INDENT:
                    self.advance()
                    self.parse_properties(prop_def.children, expect_dedent=True)
                
                target_dict[name] = prop_def
            else:
                if self.current_token().type != TokenType.IS:
                    self.error(f"Expected 'is' after property name")
                self.advance()
                
                prop_def = PropertyDef(name=name, is_container=False)
                constraint = self.parse_constraint()
                prop_def.constraint = constraint
                
                target_dict[name] = prop_def
                self.skip_trivia()
    
    def parse_constraint(self) -> Constraint:
        return self.parse_or_expr()
    
    def parse_or_expr(self) -> Constraint:
        left = self.parse_and_expr()
        
        while self.current_token().type == TokenType.OR:
            self.advance()
            right = self.parse_and_expr()
            left = Constraint("or", children=[left, right])
        
        return left
    
    def parse_and_expr(self) -> Constraint:
        left = self.parse_not_expr()
        
        while self.current_token().type == TokenType.AND:
            self.advance()
            right = self.parse_not_expr()
            left = Constraint("and", children=[left, right])
        
        return left
    
    def parse_not_expr(self) -> Constraint:
        if self.current_token().type == TokenType.NOT:
            self.advance()
            expr = self.parse_not_expr()
            return Constraint("not", children=[expr])
        return self.parse_primary_constraint()
    
    def parse_primary_constraint(self) -> Constraint:
        token = self.current_token()
        
        if token.type == TokenType.LPAREN:
            self.advance()
            constraint = self.parse_constraint()
            self.expect(TokenType.RPAREN)
            return constraint
        
        if token.type == TokenType.STRING_TYPE:
            self.advance()
            return Constraint("string")
        if token.type == TokenType.NUMBER_TYPE:
            self.advance()
            return Constraint("number")
        if token.type == TokenType.BOOLEAN_TYPE:
            self.advance()
            return Constraint("boolean")
        if token.type == TokenType.NULL:
            self.advance()
            return Constraint("null")
        if token.type == TokenType.TRUE:
            self.advance()
            return Constraint("true")
        if token.type == TokenType.FALSE:
            self.advance()
            return Constraint("false")
        
        if token.type == TokenType.STRING:
            value = token.value
            self.advance()
            return Constraint("literal", value=value)
        if token.type == TokenType.NUMBER:
            value = token.value
            self.advance()
            return Constraint("literal", value=value)
        
        if token.type == TokenType.REQUIRED:
            self.advance()
            return Constraint("required")
        if token.type == TokenType.OPTIONAL:
            self.advance()
            return Constraint("optional")
        
        if token.type == TokenType.ARRAY:
            self.advance()
            inner_type = None
            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                inner_type = self.parse_constraint()
                self.expect(TokenType.RPAREN)
            return Constraint("array", value=inner_type)
        
        if token.type == TokenType.MINIMUM:
            self.advance()
            value = self.expect(TokenType.NUMBER).value
            return Constraint("minimum", value=value)
        if token.type == TokenType.MAXIMUM:
            self.advance()
            value = self.expect(TokenType.NUMBER).value
            return Constraint("maximum", value=value)
        if token.type == TokenType.LONGER:
            self.advance()
            value = self.expect(TokenType.NUMBER).value
            return Constraint("longer", value=value)
        if token.type == TokenType.SHORTER:
            self.advance()
            value = self.expect(TokenType.NUMBER).value
            return Constraint("shorter", value=value)
        if token.type == TokenType.LARGER:
            self.advance()
            value = self.expect(TokenType.NUMBER).value
            return Constraint("larger", value=value)
        if token.type == TokenType.SMALLER:
            self.advance()
            value = self.expect(TokenType.NUMBER).value
            return Constraint("smaller", value=value)
        
        if token.type == TokenType.MATCH:
            self.advance()
            self.expect(TokenType.LPAREN)
            pattern = self.expect(TokenType.NAME).value
            self.expect(TokenType.RPAREN)
            return Constraint("match", value=pattern)
        
        if token.type == TokenType.NAME:
            name = token.value
            self.advance()
            return Constraint("type", value=name)
        
        self.error(f"Unexpected token in constraint: {token.type}")


class Validator:
    """Validate JSON against a schema."""
    
    def __init__(self, schema: Schema):
        self.schema = schema
    
    def validate(self, json_data: Any) -> Tuple[bool, List[str]]:
        """Validate JSON data. Returns (is_valid, errors)."""
        errors = []
        
        if not isinstance(json_data, dict):
            errors.append("Root must be an object")
            return False, errors
        
        self.validate_object(json_data, self.schema.properties, "$", errors, self.schema.custom_types, closed=self.schema.closed)
        return len(errors) == 0, errors
    
    def validate_object(self, obj: Dict, props: Dict[str, PropertyDef], path: str, errors: List[str], custom_types: Dict[str, PropertyDef], closed: bool = False):
        """Validate an object against expected properties."""
        seen_keys = set()
        
        for key, val in obj.items():
            seen_keys.add(key)
            
            if key in props:
                prop_def = props[key]

                if prop_def.is_container:
                    if isinstance(val, dict):
                        self.validate_object(val, prop_def.children, f"{path}.{key}", errors, custom_types)
                    else:
                        errors.append(f"{path}.{key}: Expected object, got {type(val).__name__}")
                elif prop_def.constraint:
                    self.validate_value(val, prop_def.constraint, f"{path}.{key}", errors, custom_types)
            elif closed:
                errors.append(f"{path}.{key}: Unexpected property (schema is closed)")
        
        # Check for missing required properties
        for key, prop_def in props.items():
            if key not in seen_keys:
                if prop_def.constraint and self.constraint_requires(prop_def.constraint):
                    errors.append(f"{path}.{key}: Required property missing")
    
    def constraint_requires(self, constraint: Constraint) -> bool:
        """Check if constraint requires a value."""
        if constraint.type == "required":
            return True
        if constraint.type == "and":
            return any(self.constraint_requires(c) for c in constraint.children)
        if constraint.type == "or":
            return any(self.constraint_requires(c) for c in constraint.children)
        return False
    
    def validate_value(self, value: Any, constraint: Constraint, path: str, errors: List[str], custom_types: Dict[str, PropertyDef]):
        """Validate value against constraint."""
        if not self.check_constraint(value, constraint, custom_types):
            errors.append(f"{path}: Does not satisfy constraint")
    
    def check_constraint(self, value: Any, constraint: Constraint, custom_types: Dict[str, PropertyDef]) -> bool:
        """Check if value satisfies constraint. Returns True/False."""
        if constraint.type == "string":
            return isinstance(value, str)
        if constraint.type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if constraint.type == "boolean":
            return isinstance(value, bool)
        if constraint.type == "null":
            return value is None
        if constraint.type == "true":
            return value is True
        if constraint.type == "false":
            return value is False
        if constraint.type == "literal":
            return value == constraint.value
        if constraint.type == "required":
            return value is not None
        if constraint.type == "optional":
            return True
        if constraint.type == "and":
            for child in constraint.children:
                if not self.check_constraint(value, child, custom_types):
                    return False
            return True
        if constraint.type == "or":
            for child in constraint.children:
                if self.check_constraint(value, child, custom_types):
                    return True
            return False
        if constraint.type == "not":
            return not self.check_constraint(value, constraint.children[0], custom_types)
        if constraint.type == "array":
            if not isinstance(value, list):
                return False
            if constraint.value:
                for item in value:
                    if not self.check_constraint(item, constraint.value, custom_types):
                        return False
            return True
        if constraint.type == "minimum":
            return isinstance(value, (int, float)) and value >= constraint.value
        if constraint.type == "maximum":
            return isinstance(value, (int, float)) and value <= constraint.value
        if constraint.type == "longer":
            return isinstance(value, str) and len(value) > constraint.value
        if constraint.type == "shorter":
            return isinstance(value, str) and len(value) < constraint.value
        if constraint.type == "larger":
            return isinstance(value, (int, float)) and value > constraint.value
        if constraint.type == "smaller":
            return isinstance(value, (int, float)) and value < constraint.value
        if constraint.type == "match":
            return isinstance(value, str) and re.match(constraint.value, value) is not None
        if constraint.type == "type":
            custom_type_name = constraint.value
            if custom_type_name in custom_types:
                if isinstance(value, dict):
                    temp_errors = []
                    self.validate_object(value, custom_types[custom_type_name].children, "temp", temp_errors, custom_types)
                    return len(temp_errors) == 0
            return False
        
        return True


def parse_and_validate(schema_text: str, json_text: str) -> Tuple[bool, List[str]]:
    """Function to call"""
    parser = Parser(schema_text)
    schema = parser.parse()
    
    json_data = json.loads(json_text)
    
    validator = Validator(schema)
    is_valid, errors = validator.validate(json_data)
    
    return is_valid, errors
