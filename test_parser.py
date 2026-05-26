from parser import parse_and_validate, Parser
import json

passed_tests_counter = 0
def test_case(name, schema_text, json_text, should_be_valid):
    """Test a single case."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")
    
    try:
        is_valid, errors = parse_and_validate(schema_text, json_text)
        
        if is_valid == should_be_valid:
            print("✅ PASS")
            global passed_tests_counter
            passed_tests_counter += 1
        else:
            print("❌ FAIL")
            print(f"  Expected: {should_be_valid}, Got: {is_valid}")
        
        print(f"Valid: {is_valid}")
        if errors:
            print(f"Errors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()


# Test 1: Simple constraint
test_case(
    "Simple string constraint",
    "name is string and required",
    '{"name": "Alice"}',
    True
)

# Test 2: Type mismatch
test_case(
    "Type mismatch",
    "age is number",
    '{"age": "not a number"}',
    False
)

# Test 3: Nested object
test_case(
    "Nested object with custom type",
    """
is defined Address:
    street is string and required
    city is string and required

person:
    name is string and required
    address is Address and required
""",
    '{"person": {"name": "Bob", "address": {"street": "Main St", "city": "NYC"}}}',
    True
)

# Test 4: Array constraint
test_case(
    "Array of strings",
    "hobbies is array(string) and required",
    '{"hobbies": ["reading", "coding", "gaming"]}',
    True
)

# Test 5: Array with wrong type
test_case(
    "Array with wrong element type",
    "hobbies is array(string) and required",
    '{"hobbies": ["reading", 123, "gaming"]}',
    False
)

# Test 6: Range constraints
test_case(
    "Range validation",
    "age is number and required and minimum 0 and maximum 150",
    '{"age": 42}',
    True
)

# Test 7: Range violation
test_case(
    "Range violation",
    "age is number and required and minimum 0 and maximum 150",
    '{"age": 200}',
    False
)

# Test 8: String length constraints
test_case(
    "String length constraints",
    "password is string and required and longer 7 and shorter 50",
    '{"password": "MySecurePassword123"}',
    True
)

# Test 9: Regex validation
test_case(
    "Regex pattern matching",
    'email is string and required and match([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,})',
    '{"email": "user@example.com"}',
    True
)

# Test 10: Logic operators (or)
test_case(
    "Logic OR constraint",
    'status is ("active" or "inactive" or "pending")',
    '{"status": "active"}',
    True
)

# Test 11: Missing required field
test_case(
    "Missing required field",
    "name is string and required",
    '{}',
    False
)

# Test 12: Optional field
test_case(
    "Optional field can be missing",
    "nickname is string and optional",
    '{}',
    True
)

# Test 13: Open schema (additional properties allowed)
test_case(
    "Open schema allows extra properties",
    "id is number and required",
    '{"id": 42, "extra": "field"}',
    True
)

print(f"\n{'=' * 60}")
print(f"{passed_tests_counter} of 13 Tests Passed!")
print(f"{'=' * 60}")
