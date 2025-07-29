"""
JSDoc Parser - A Python package for parsing JSDoc comment blocks.

This package provides functionality to parse JavaScript documentation comments
(JSDoc) into structured Python objects using Pydantic BaseModel.

Main Functions:
    parse: Parse a JSDoc comment string into structured data

Example:
    >>> from jsdoc_parser import parse
    >>> jsdoc_string = '''/**
    ...  * Adds two numbers together.
    ...  * @param {number} a - The first number
    ...  * @param {number} b - The second number  
    ...  * @returns {number} The sum of a and b
    ...  */'''
    >>> result = parse(jsdoc_string)
    >>> print(result.params[0].name)  # 'a'
"""

from .parser import parse
from .models import (
    JSDocComment,
    Parameter,
    ReturnValue,
    TypeDef,
    Property,
    Example,
    Throws,
    Description,
)

__version__ = "1.0.2"
__all__ = [
    "parse",
    "JSDocComment", 
    "Parameter",
    "ReturnValue",
    "TypeDef",
    "Property", 
    "Example",
    "Throws",
    "Description",
]