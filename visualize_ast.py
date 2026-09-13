import sys
from parser import Parser, Schema, PropertyDef, Constraint
from lexer import Lexer, TokenType

def print_tree(node, prefix="", is_last=True, is_root=False):
    marker = "" if is_root else ("└── " if is_last else "├── ")
    
    if isinstance(node, Schema):
        print(f"{prefix}{marker}Schema (root_type={node.root_type}, closed={node.closed})")
        prefix += "" if is_root else ("    " if is_last else "│   ")
        
        children = []
        if node.custom_types:
            children.append(("Custom Types", list(node.custom_types.values())))
        if node.properties:
            children.append(("Properties", list(node.properties.values())))
            
        for i, (label, items) in enumerate(children):
            is_last_group = (i == len(children) - 1)
            group_marker = "└── " if is_last_group else "├── "
            print(f"{prefix}{group_marker}{label}")
            sub_prefix = prefix + ("    " if is_last_group else "│   ")
            for j, item in enumerate(items):
                print_tree(item, sub_prefix, j == len(items) - 1)
                
    elif isinstance(node, PropertyDef):
        props = []
        if node.is_container:
            props.append("container")
        if node.closed:
            props.append("closed")
        props_str = f" [{', '.join(props)}]" if props else ""
            
        print(f"{prefix}{marker}Property: '{node.name}'{props_str}")
        prefix += "    " if is_last else "│   "
        
        children = []
        if node.constraint:
            children.append(node.constraint)
        if node.children:
            children.extend(node.children.values())
            
        for i, child in enumerate(children):
            print_tree(child, prefix, i == len(children) - 1)
            
    elif isinstance(node, Constraint):
        val_str = f" (value={node.value!r})" if node.value is not None else ""
        print(f"{prefix}{marker}Constraint: {node.type}{val_str}")
        prefix += "    " if is_last else "│   "
        
        for i, child in enumerate(node.children):
            print_tree(child, prefix, i == len(node.children) - 1)

import textwrap

def visualize_tokens(schema_text):
    print("Token Stream:")
    print("=" * 50)
    lexer = Lexer(schema_text)
    tokens = lexer.tokenize()
    for t in tokens:
        val = f" {t.value!r}" if t.value is not None else ""
        print(f"[{t.line}:{t.col}] {t.type.name}{val}")
    print()

def main():
    schema_text = textwrap.dedent("""
    is schema "https://www.ur.de/jdt-schema"
    is type object

    Name is string, required
    Age is number, required
    Student: 
        StudentID is number, required
        Major is string, required
        Level is string, required


    """).strip()
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            schema_text = f.read()
            
    print("Visualizing Parsing & AST")
    print("=========================\n")
    
    visualize_tokens(schema_text)
    
    parser = Parser(schema_text)
    try:
        schema = parser.parse()
        print("AST Visualization:")
        print("=" * 50)
        print_tree(schema, is_root=True)
    except Exception as e:
        print(f"Error parsing schema: {e}")

if __name__ == "__main__":
    main()
