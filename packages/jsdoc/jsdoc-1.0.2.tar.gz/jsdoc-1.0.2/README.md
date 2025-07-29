# JSDoc Parser

A professional Python package for parsing JavaScript documentation comments (JSDoc) into structured Pydantic BaseModel objects.

## Features

- **Comprehensive JSDoc Support**: Parses all major JSDoc tags including `@param`, `@returns`, `@typedef`, `@property`, `@example`, and `@throws`
- **Multiple TypeDef Support**: Parse multiple `@typedef` definitions from single or separate comment blocks
- **Type-Safe**: Built with Pydantic BaseModel for robust data validation and type safety
- **Union Types**: Full support for union types like `string|number|null`
- **Optional Parameters**: Handles optional parameters with bracket syntax `[param]`
- **Code Extraction**: Optionally extracts JavaScript code that follows JSDoc comments
- **Professional API**: Simple `parse()` function interface with detailed structured output

## Installation

```bash
pip install jsdoc
```

## Quick Start

```python
from jsdoc import parse

# Parse a JSDoc comment
jsdoc_string = '''/**
 * Adds two numbers together.
 * @param {number} a - The first number
 * @param {number} b - The second number
 * @returns {number} The sum of a and b
 * @example
 * add(1, 2); // returns 3
 */
function add(a, b) {
    return a + b;
}'''

result = parse(jsdoc_string)

# Access structured data
print(result.description.summary)  # "Adds two numbers together."
print(result.params[0].name)       # "a"
print(result.params[0].types)      # ["number"]
print(result.returns[0].types)     # ["number"]
print(result.examples[0].code)     # "add(1, 2); // returns 3"
print(result.code)                 # "function add(a, b) {\\n    return a + b;\\n}"
```

## Supported JSDoc Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `@param` | Function parameter | `@param {string} name - User's name` |
| `@returns/@return` | Return value | `@returns {number} Sum of a and b` |
| `@typedef` | Custom type definition | `@typedef {Object} User` |
| `@property` | Object property | `@property {number} age - User's age` |
| `@example` | Usage example | `@example doSomething(123);` |
| `@throws` | Possible exceptions | `@throws {Error} If input is invalid` |

## Output Structure

The `parse()` function returns a `JSDocComment` object with the following structure:

```python
{
    "description": {
        "full": "Complete description text...",
        "summary": "Brief summary sentence."
    },
    "params": [
        {
            "types": ["string"],
            "name": "param_name", 
            "description": "Parameter description",
            "optional": False
        }
    ],
    "returns": [
        {
            "types": ["number"],
            "description": "Return value description"
        }
    ],
    "examples": [
        {
            "code": "example_code();",
            "description": None
        }
    ],
    "throws": [
        {
            "types": ["Error"],
            "description": "Exception description"
        }
    ],
    "typedefs": [
        {
            "types": ["Object"],
            "name": "CustomType",
            "description": "Type description",
            "properties": [...]
        }
    ],
    "properties": [...],
    "code": "function code() { ... }",
    "raw_comment": "/** original comment */"
}
```

## Advanced Usage

### Parsing Without Code Extraction

```python
result = parse(jsdoc_string, include_code=False)
# result.code will be None
```

### Handling TypeDefs with Properties

```python
jsdoc = '''/**
 * @typedef {object} User
 * @property {string} name - User's name
 * @property {number} age - User's age
 * @property {string|null} email - User's email (optional)
 */'''

result = parse(jsdoc, include_code=False)
print(result.typedefs[0].name)           # "User"
print(result.typedefs[0].properties[0].name)     # "name"
print(result.typedefs[0].properties[0].types)    # ["string"]
print(result.typedefs[0].properties[2].types)    # ["string", "null"]
```

### Multiple TypeDef Definitions

Parse multiple typedef definitions from a single comment block:

```python
jsdoc = '''/**
 * @typedef {object} User
 * @property {string} name - User's name
 * 
 * @typedef {object} Role
 * @property {string} name - Role name
 * @property {string[]} permissions - Role permissions
 * 
 * @typedef {string} Status - User status
 */'''

result = parse(jsdoc, include_code=False)
print(len(result.typedefs))          # 3
print(result.typedefs[0].name)       # "User"
print(result.typedefs[1].name)       # "Role"
print(result.typedefs[2].name)       # "Status"
```

Or from separate comment blocks:

```python
jsdoc = '''/**
 * @typedef {object} Product
 * @property {string} id - Product identifier
 * @property {number} price - Product price
 */

/**
 * @typedef {object} Category
 * @property {string} name - Category name
 * @property {Product[]} products - Products in category
 */

function getProducts() {
    return products;
}'''

result = parse(jsdoc)
print(len(result.typedefs))          # 2
print(result.typedefs[0].name)       # "Product"
print(result.typedefs[1].name)       # "Category"
print(result.code)                   # "function getProducts() { ... }"
```

### Optional Parameters

```python
jsdoc = '''/**
 * @param {string} name - Required parameter
 * @param {number} [age] - Optional parameter
 * @param {string} [email=user@example.com] - Optional with default
 */'''

result = parse(jsdoc, include_code=False)
print(result.params[0].optional)  # False
print(result.params[1].optional)  # True
print(result.params[2].optional)  # True
```

### Union Types

```python
jsdoc = '''/**
 * @param {string|number|boolean} value - Multi-type parameter
 * @returns {User|null} User object or null
 */'''

result = parse(jsdoc, include_code=False)
print(result.params[0].types)    # ["string", "number", "boolean"]
print(result.returns[0].types)   # ["User", "null"]  
```

## API Reference

### `parse(jsdoc_string: str, include_code: bool = True) -> JSDocComment`

Parse a JSDoc comment string into a structured object.

**Parameters:**
- `jsdoc_string` (str): JSDoc comment string, typically wrapped in `/** */`
- `include_code` (bool): Whether to extract JavaScript code following the comment

**Returns:**
- `JSDocComment`: Structured representation of the parsed JSDoc

**Raises:**
- `ValueError`: If the input is not a valid JSDoc comment format

### Data Models

All returned objects are Pydantic BaseModel instances with full type validation:

- `JSDocComment`: Main container for all parsed data
- `Description`: Comment description with full text and summary
- `Parameter`: Function parameter information
- `ReturnValue`: Return value information  
- `TypeDef`: Custom type definition
- `Property`: Object property definition
- `Example`: Usage example
- `Throws`: Exception information

## Error Handling

The parser will raise `ValueError` for invalid input:

```python
try:
    result = parse("invalid comment")
except ValueError as e:
    print(f"Parse error: {e}")
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yunfanye/jsdoc
cd jsdoc
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest -v  # verbose output
pytest --cov=jsdoc_parser  # with coverage
```

### Code Formatting

```bash
black jsdoc_parser/
isort jsdoc_parser/
flake8 jsdoc_parser/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## Changelog

### v1.0.2
- **BREAKING CHANGE**: Changed `typedef` field to `typedefs` (List[TypeDef]) in JSDocComment model
- Added support for multiple typedef definitions in single comment block
- Added support for parsing separate typedef comment blocks
- Improved comment block selection logic for mixed typedef and function documentation
- Enhanced code extraction to work correctly with multiple comment blocks
- Added comprehensive tests for multiple typedef scenarios
- Updated documentation with multiple typedef examples

### v1.0.1
- Bug fixes and improvements

### v1.0.0
- Initial release
- Support for all major JSDoc tags
- Pydantic BaseModel integration
- Comprehensive test suite
- Professional documentation
