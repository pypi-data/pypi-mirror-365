"""
Pydantic models for representing JSDoc comment structures.

This module defines the data models used to represent parsed JSDoc comments
as structured Python objects. Each model corresponds to a specific JSDoc tag
or component.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Description(BaseModel):
    """
    Represents the description section of a JSDoc comment.
    
    Attributes:
        full: The complete description text including all details
        summary: A brief summary, typically the first sentence or line
    """
    full: str = Field(description="The complete description text")
    summary: str = Field(description="A brief summary of the description")


class Parameter(BaseModel):
    """
    Represents a @param tag in JSDoc.
    
    Attributes:
        types: List of possible parameter types (e.g., ['string', 'number'])
        name: The parameter name
        description: Description of what the parameter represents
        optional: Whether the parameter is optional (indicated by [] syntax)
    """
    types: List[str] = Field(description="List of possible parameter types")
    name: str = Field(description="The parameter name")
    description: str = Field(description="Parameter description")
    optional: bool = Field(default=False, description="Whether parameter is optional")


class ReturnValue(BaseModel):
    """
    Represents a @returns or @return tag in JSDoc.
    
    Attributes:
        types: List of possible return types
        description: Description of what is returned
    """
    types: List[str] = Field(description="List of possible return types")
    description: str = Field(description="Description of the return value")


class Property(BaseModel):
    """
    Represents a @property tag in JSDoc, typically used within @typedef.
    
    Attributes:
        types: List of possible property types
        name: The property name
        description: Description of the property
        optional: Whether the property is optional
    """
    types: List[str] = Field(description="List of possible property types")
    name: str = Field(description="The property name")
    description: str = Field(description="Property description")
    optional: bool = Field(default=False, description="Whether property is optional")


class TypeDef(BaseModel):
    """
    Represents a @typedef tag in JSDoc for defining custom types.
    
    Attributes:
        types: The base types this typedef extends (e.g., ['Object'])
        name: The name of the custom type
        description: Description of the type (optional)
        properties: List of properties if this is an object type
    """
    types: List[str] = Field(description="Base types for the typedef")
    name: str = Field(description="Name of the custom type")
    description: Optional[str] = Field(default=None, description="Type description")
    properties: List[Property] = Field(default_factory=list, description="Type properties")


class Example(BaseModel):
    """
    Represents an @example tag in JSDoc.
    
    Attributes:
        code: The example code or usage
        description: Optional description of the example
    """
    code: str = Field(description="The example code")
    description: Optional[str] = Field(default=None, description="Example description")


class Throws(BaseModel):
    """
    Represents a @throws tag in JSDoc.
    
    Attributes:
        types: List of exception/error types that can be thrown
        description: Description of when/why the exception is thrown
    """
    types: List[str] = Field(description="List of exception types")
    description: str = Field(description="Description of the exception condition")


class JSDocComment(BaseModel):
    """
    Represents a complete parsed JSDoc comment block.
    
    This is the main model returned by the parse() function, containing all
    parsed JSDoc tags and content.
    
    Attributes:
        description: The main description of the documented item
        params: List of @param tags
        returns: List of @returns/@return tags  
        typedefs: List of @typedef definitions
        properties: List of @property tags (usually within @typedef)
        examples: List of @example tags
        throws: List of @throws tags
        code: Any associated code that follows the JSDoc comment
        raw_comment: The original unparsed comment string
    """
    description: Optional[Description] = Field(default=None, description="Main description")
    params: List[Parameter] = Field(default_factory=list, description="Function parameters")
    returns: List[ReturnValue] = Field(default_factory=list, description="Return values")
    typedefs: List[TypeDef] = Field(default_factory=list, description="Type definitions")
    properties: List[Property] = Field(default_factory=list, description="Object properties")
    examples: List[Example] = Field(default_factory=list, description="Usage examples")
    throws: List[Throws] = Field(default_factory=list, description="Possible exceptions")
    code: Optional[str] = Field(default=None, description="Associated code following the comment")
    raw_comment: str = Field(description="Original comment string")
    
    model_config = ConfigDict(
        extra='forbid',  # Don't allow extra fields
        validate_assignment=True  # Validate on assignment
    )