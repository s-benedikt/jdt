# JDT Schema overview

JSON Document Type Schema Language overview. Based on the TOON Schema overview https://toonformat.dev/guide/format-overview.

---
## Data Model
- Primitive: String, number, boolean, and `null`
- Objects and properties (called containers)
- Unstructured arrays
- Defined Data Types

A number can be a floating-point value.

## Root 

If not specified, the root object exists without explicit declaration.
There are certain parameters that the root object can be specified with the keyword `is`.
- schema specifies the URI for a parent schema
- version specifies the URI of the version used
- owner specifies the owner's URL
- type specifies the type of the root object

All root parameters are optional. The defaults for root parameters are
- no root schema,
- newest stable version,
- `null`, and
- object

respectively.

Comments are marked by `"""` and are valid until closed with the same sequence.

## Valid Names

Names can contain any Unicode character except for `"""`  and cannot be `is` or contain a space.
Users can use any breakout character for `is`: like `#is, \is, $is, ...`. It can't be just `is`.

Example for valid names:
```
name
key
Straße
København
13.03.2004
new1
wow!?
new_Name
=§%$&@€
isNull"
null
gän"se"füß"chen
#name
"name"
#is
\is
is$
```
Not valid names:
```
is
b"""1
n a m e
```
It’s the developer's responsibility to ensure their names don’t violate JSON’s name requirements.

A colon `:` at the end of a name, followed by a return signalizes a container. A key's name ends with the absence of a colon and a space.
The indentation `whitespace` encodes the parent.
```
name:           <-- This is a container
name            <-- This is a key
=§%$&@€:        <-- This is a container
=§%$&@€         <-- This is a key

parent:
    child       <-- Indent defines hierarchy
```


## Constraints

JDT documents are validated against a JDT Schema with constraints.
A constraint starts with `is`.

Simple constraint:
- true 
- false
- null
- number
- boolean
- string


Occurrence constraints:
- required: exactly one occurrence
- optional: zero or one occurrence

If not specified, the default is `optional`.

Operator constraints:
- and
- or
- not

The `or` operator requires parentheses in complex constraint schemas and always evaluates its immediate neighbours.
There is no hierarchy of operators:
```
is (true and required) or (false and optional)
```
does not make any sense and is not allowed.
Despite the common ranking, JDT will evaluate logic from left to right.
```
... is a and (b or c) and d and e
```
evaluates to:
$$
a \land (b \lor c ) \land d \land e
$$



Array constraints:
- array
- array(datatype)
- array(array(datatype))

Arrays can be nested. If no datatype is specified, all datatypes validate. 
As of now, constraints can't be used inside arrays.

Value and length constraints:
- minimum [number]
- maximum [number]
- longer [number]
- shorter [number]
- larger [number]
- smaller [number]

Equality constraints:
- number
- "string"
- boolean
- null

Regex constraints:
- match(regex)

Regex and strings must not contain `"""`.

Undefined constraints are not used for a key in the schema, but rather for unknown, potential keys:
- closed
- open
- unordered
- ordered

JDT enforces an open, unordered schema as the standard. Any key that is not defined in the schema is considered valid. If a key is not in order, as with the schema, the document is considered valid unless stated otherwise. Undefined constraints can only be defined once per container at its beginning or for the entire document.

## Defined Data Types

JDT allows custom-defined data types with the keyword `defined`:
```
is defined Address:
    street is string
    number is number and minimum 1
    zip is number and longer 4 and shorter 6

user:
    home is Address
```

The name of the custom data type has to follow the same rules as other names. They must not be the same as an already existing key (case sensitive).
A `defined` block is not a container.

## Examples
Simple Objects and Constraints:
```
id is number           """ This is a comment """
name is string
```
Nested Objects and Constraints:
```
user:
    id is number and required and minimum 0
    name is string and optional
```
Complex Objects and Constraints:
```
is type object
user: 
    is closed and ordered
    id is number and required and not null
    name is required and not boolean
    age is optional and (number or null)
    hobbies is array(string) and required
    eyecolor is "blue" or "green" or "brown"

```

Realization of the Complex Objects and Constraints Schema:
```
{                           <-- This is the root object
  "user": {                 <-- This is a container
    "id": 1,                <-- This is a key value pair
    "name": "Jane Doe",
    "age": 28,
    "hobbies": [            <-- This is an array consisting of strings
      "reading",
      "coding",
      "hiking"
    ],
    "eyecolor": "blue"      
  }
}
```
This is valid. The following is not:
```
{
  "user": {                
    "id": null,             <-- Violates Schema `not null`
    "name": true,           <-- Violates Schema `not boolean`
    "age": "twenty",        <-- Violates Schema `(number or null)`
    "sex": "female",        <-- Violates Schema key
    "height": 172           <-- Violates Schema `closed`
                            <-- Violates Schema hobbies `required`
  }
}
```

## Longer Example

```
is schema https://www.uni-regensburg.de/jdt-schema
is version https://www.jdt-schema.com/version/1
is owner https://www.uni-regensburg.de
is type object

is closed and ordered

is defined Address:
    street is string
    number is number and minimum 1
    zip is number and longer 4 and shorter 6

is defined Payment:
    number is number and required and minimum 13 and maximum 19
    name is string and required
    expires is match(\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])\b) and required
    cvv is number and required and minimum 3 and maximum 4

is defined Year:
    year is number and larger 2020 and smaller 2030

user:
    id is number and required and minimum 0
    name is string and longer 0 and required
    address is Address and required
    sex is string and optional
    height is number
    eyecolor is string and "blue" or "green" or "brown" and optional
    creditCard is Payment and required
    subscribed is boolean
    memberSince is Year
```

Validates:

```
{
  "$schema": "https://www.uni-regensburg.de/jdt-schema",
  "$version": "https://www.jdt-schema.com/version/1",
  "owner": "https://www.uni-regensburg.de",
  "id": 101,
  "name": "Jane Doe",
  "address": {
    "street": "Universitätsstraße",
    "number": 31,
    "zip": 93053
  }
  "sex": "female",
  "height": 172,
  "eyecolor": "green",
  "creditCard": {
    "number": 4532123456789012,
    "name": "Jane Doe",
    "expires": "14/08",
    "cvv": 987
  }
  "subscribed": true,
  "memberSince": {
    "year": 2025

}