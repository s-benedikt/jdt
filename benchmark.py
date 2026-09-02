import time
import json
import traceback

try:
    import jsonschema
except ImportError:
    print("Error: The 'jsonschema' package is required for this benchmark.")
    print("Please install it using: pip install jsonschema")
    exit(1)

try:
    import jsonschema_rs
except ImportError:
    jsonschema_rs = None
    print("Warning: 'jsonschema_rs' package is not installed. Skipping its benchmark.")

try:
    import fastjsonschema
except ImportError:
    fastjsonschema = None
    print("Warning: 'fastjsonschema' package is not installed. Skipping its benchmark.")

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

if jsonschema_rs:
    jsonschema_rs_compiled = jsonschema_rs.Draft7Validator(json_schema_obj)

if fastjsonschema:
    fastjsonschema_compiled = fastjsonschema.compile(json_schema_obj)

# --- PARSING/COMPILATION BENCHMARK ---
ITERATIONS_PARSE = 1000
print(f"\n--- Parsing/Compilation ({ITERATIONS_PARSE} iterations) ---")

start_time = time.perf_counter()
for _ in range(ITERATIONS_PARSE):
    parser = Parser(jdt_schema_text)
    _ = parser.parse()
jdt_parse_time = (time.perf_counter() - start_time) / ITERATIONS_PARSE * 1000

start_time = time.perf_counter()
for _ in range(ITERATIONS_PARSE):
    jsonschema.Draft7Validator.check_schema(json_schema_obj)
jsonschema_parse_time = (time.perf_counter() - start_time) / ITERATIONS_PARSE * 1000

print(f"JDT Lex+Parse:       {jdt_parse_time:.4f} ms")
print(f"JSON Schema (py):    {jsonschema_parse_time:.4f} ms")

if jsonschema_rs:
    start_time = time.perf_counter()
    for _ in range(ITERATIONS_PARSE):
        jsonschema_rs.Draft7Validator(json_schema_obj)
    jsonschema_rs_parse_time = (time.perf_counter() - start_time) / ITERATIONS_PARSE * 1000
    print(f"JSON Schema (rs):    {jsonschema_rs_parse_time:.4f} ms")

if fastjsonschema:
    start_time = time.perf_counter()
    for _ in range(ITERATIONS_PARSE):
        fastjsonschema.compile(json_schema_obj)
    fastjsonschema_parse_time = (time.perf_counter() - start_time) / ITERATIONS_PARSE * 1000
    print(f"fastjsonschema:      {fastjsonschema_parse_time:.4f} ms")

# --- VALIDATION BENCHMARK (Different Document Sizes) ---
ITERATIONS_VAL = 100
document_sizes = [10, 100, 1000, 5000]

print("\n--- Validation (Varying Document Size) ---")
print(f"{'Size (Users)':<15} | {'JDT (ms)':<12} | {'jsonschema (ms)':<16} | {'jsonschema_rs (ms)':<20} | {'fastjsonschema (ms)':<20}")
print("-" * 95)

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
    jdt_val_time = (time.perf_counter() - start_time) / ITERATIONS_VAL * 1000

    start_time = time.perf_counter()
    for _ in range(ITERATIONS_VAL):
        list(json_schema_compiled.iter_errors(payload)) 
    jsonschema_val_time = (time.perf_counter() - start_time) / ITERATIONS_VAL * 1000

    jsonschema_rs_val_time = 0
    if jsonschema_rs:
        start_time = time.perf_counter()
        for _ in range(ITERATIONS_VAL):
            jsonschema_rs_compiled.is_valid(payload)
        jsonschema_rs_val_time = (time.perf_counter() - start_time) / ITERATIONS_VAL * 1000

    fastjsonschema_val_time = 0
    if fastjsonschema:
        start_time = time.perf_counter()
        for _ in range(ITERATIONS_VAL):
            fastjsonschema_compiled(payload)
        fastjsonschema_val_time = (time.perf_counter() - start_time) / ITERATIONS_VAL * 1000

    rs_str = f"{jsonschema_rs_val_time:<20.4f}" if jsonschema_rs else f"{'N/A':<20}"
    fast_str = f"{fastjsonschema_val_time:<20.4f}" if fastjsonschema else f"{'N/A':<20}"
    print(f"{num_users:<15} | {jdt_val_time:<12.4f} | {jsonschema_val_time:<16.4f} | {rs_str} | {fast_str}")
