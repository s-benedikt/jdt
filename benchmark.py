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
from parser import Parser, Validator, parse_and_validate

print("Setting up schemas and test data...")

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

NUM_USERS = 1000
payload = {
    "users": [
        {"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "active": True}
        for i in range(NUM_USERS)
    ]
}
# sanity check
try:
    jsonschema.validate(instance=payload, schema=json_schema_obj)
    
    jdt_parser = Parser(jdt_schema_text)
    jdt_schema_parsed = jdt_parser.parse()
    jdt_validator = Validator(jdt_schema_parsed)
    is_valid, errs = jdt_validator.validate(payload)
    if not is_valid:
        print("Sanity check failed for JDT:", errs)
        exit(1)
        
except Exception as e:
    print("Sanity check failed:", e)
    traceback.print_exc()
    exit(1)


print("Starting benchmark...\n")

# --- PARSING/COMPILATION BENCHMARK ---
ITERATIONS_PARSE = 1000

print(f"--- Parsing/Compilation ({ITERATIONS_PARSE} iterations) ---")

start_time = time.perf_counter()
for _ in range(ITERATIONS_PARSE):
    parser = Parser(jdt_schema_text)
    _ = parser.parse()
jdt_parse_time = time.perf_counter() - start_time

start_time = time.perf_counter()
for _ in range(ITERATIONS_PARSE):
    # For JSON schema, the compilation step is checking the schema structure
    jsonschema.Draft7Validator.check_schema(json_schema_obj)
jsonschema_parse_time = time.perf_counter() - start_time

print(f"JDT Lex+Parse: {jdt_parse_time:.4f} seconds")
print(f"JSON Schema Check:   {jsonschema_parse_time:.4f} seconds")
if jdt_parse_time > jsonschema_parse_time:
    print(f"JSON Schema is {jdt_parse_time/jsonschema_parse_time:.1f}x faster at startup.\n")
else:
    print(f"JDT is {jsonschema_parse_time/jdt_parse_time:.1f}x faster at startup.\n")


# --- VALIDATION BENCHMARK ---
ITERATIONS_VAL = 100

print(f"--- Validation of {NUM_USERS} elements ({ITERATIONS_VAL} iterations) ---")

start_time = time.perf_counter()
for _ in range(ITERATIONS_VAL):
    jdt_validator.validate(payload)
jdt_val_time = time.perf_counter() - start_time

start_time = time.perf_counter()
# Pre-compile the validator for a fair comparison, as jsonschema.validate() compiles every time
json_schema_compiled = jsonschema.Draft7Validator(json_schema_obj)
for _ in range(ITERATIONS_VAL):
    # list() forces the generator to evaluate all errors if we were using iter_errors
    list(json_schema_compiled.iter_errors(payload)) 
jsonschema_val_time = time.perf_counter() - start_time

print(f"JDT Validation:       {jdt_val_time:.4f} seconds")
print(f"JSON Schema Valid.:   {jsonschema_val_time:.4f} seconds")

if jdt_val_time > jsonschema_val_time:
    print(f"JSON Schema is {jdt_val_time/jsonschema_val_time:.1f}x faster at validation.")
else:
    print(f"JDT is {jsonschema_val_time/jdt_val_time:.1f}x faster at validation.")
