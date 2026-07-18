import time
import json
import traceback

try:
    import jsonschema
except ImportError:
    print("Error: The 'jsonschema' package is required for this benchmark.")
    print("Please install it using: pip install jsonschema")
    exit(1)

# Import JDT
from parser import Parser, Validator

print("Setting up schemas...")

# 1. Base Schema Definition
jdt_schema_text = r'''
define User:
    id is number and required
    name is string and required
    email is string and required and match("""[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}""")
    active is boolean and optional

users is array(User) and required
'''

json_schema_obj = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "pattern": "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"},
                    "active": {"type": "boolean"}
                },
                "required": ["id", "name", "email"]
            }
        }
    },
    "required": ["users"]
}

# Pre-parse/compile schemas for validation benchmark
jdt_parser = Parser(jdt_schema_text)
jdt_schema_parsed = jdt_parser.parse()
jdt_validator = Validator(jdt_schema_parsed)
json_schema_compiled = jsonschema.Draft7Validator(json_schema_obj)

# --- PARSING/COMPILATION BENCHMARK ---
ITERATIONS_PARSE = 1000
print(f"\n--- Parsing/Compilation ({ITERATIONS_PARSE} iterations) ---")

start_time = time.perf_counter()
for _ in range(ITERATIONS_PARSE):
    parser = Parser(jdt_schema_text)
    _ = parser.parse()
jdt_parse_time = time.perf_counter() - start_time

start_time = time.perf_counter()
for _ in range(ITERATIONS_PARSE):
    jsonschema.Draft7Validator.check_schema(json_schema_obj)
jsonschema_parse_time = time.perf_counter() - start_time

print(f"JDT Lex+Parse: {jdt_parse_time:.4f} seconds")
print(f"JSON Schema Check:   {jsonschema_parse_time:.4f} seconds")
if jdt_parse_time > jsonschema_parse_time:
    print(f"JSON Schema is {jdt_parse_time/jsonschema_parse_time:.1f}x faster at startup.\n")
else:
    print(f"JDT is {jsonschema_parse_time/jdt_parse_time:.1f}x faster at startup.\n")


# --- VALIDATION BENCHMARK (Different Document Sizes) ---
ITERATIONS_VAL = 100
document_sizes = [10, 100, 1000, 5000]

print("--- Validation (Varying Document Size) ---")
print(f"{'Size (Users)':<15} | {'JDT (s)':<12} | {'JSON Schema (s)':<15} | {'Speedup'}")
print("-" * 65)

for num_users in document_sizes:
    payload = {
        "users": [
            {"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "active": True}
            for i in range(num_users)
        ]
    }
    
    # Validation Benchmark
    start_time = time.perf_counter()
    for _ in range(ITERATIONS_VAL):
        jdt_validator.validate(payload)
    jdt_val_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    for _ in range(ITERATIONS_VAL):
        list(json_schema_compiled.iter_errors(payload)) 
    jsonschema_val_time = time.perf_counter() - start_time

    if jdt_val_time > jsonschema_val_time:
        speedup = f"JSONSchema {jdt_val_time/jsonschema_val_time:.1f}x faster"
    else:
        speedup = f"JDT {jsonschema_val_time/jdt_val_time:.1f}x faster"
        
    print(f"{num_users:<15} | {jdt_val_time:<12.4f} | {jsonschema_val_time:<15.4f} | {speedup}")

