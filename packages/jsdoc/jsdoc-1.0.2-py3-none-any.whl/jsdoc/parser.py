"""
JSDoc comment parser implementation.

This module contains the core parsing logic for converting JSDoc comment strings
into structured Python objects. It uses regular expressions to extract different
JSDoc tags and their associated content.
"""

import re
from typing import List, Optional
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


class JSDocParser:
    """
    Parser class for JSDoc comments.
    
    This class contains all the parsing logic and regular expressions needed
    to extract JSDoc tags and content from comment strings.
    """
    
    # Regular expressions for different JSDoc patterns
    COMMENT_BLOCK_PATTERN = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)
    PARAM_PATTERN = re.compile(r'@param\s+\{([^}]+)\}\s+(\[?([^[\]\s-]+(?:=[^[\]]*)?)\]?)\s*-?\s*(.*)', re.MULTILINE)
    RETURN_PATTERN = re.compile(r'@returns?\s+\{([^}]+)\}\s*-?\s*(.*)', re.MULTILINE)
    TYPEDEF_PATTERN = re.compile(r'@typedef\s+\{([^}]+)\}\s+([^\s]+)(?:\s*-?\s*([^@]*))?', re.MULTILINE)
    PROPERTY_PATTERN = re.compile(r'@property\s+\{([^}]+)\}\s+(\[?([^[\]\s-]+(?:=[^[\]]*)?)\]?)\s*-?\s*(.*)', re.MULTILINE)
    EXAMPLE_PATTERN = re.compile(r'@example\s*\n?(.*?)(?=@\w+|\*/|$)', re.DOTALL | re.MULTILINE)
    THROWS_PATTERN = re.compile(r'@throws\s+\{([^}]+)\}\s*-?\s*(.*)', re.MULTILINE)
    
    @staticmethod
    def _clean_comment_content(content: str) -> str:
        """
        Clean up JSDoc comment content by removing comment markers and asterisks.
        
        Args:
            content: Raw comment content with /* */ and * markers
            
        Returns:
            Cleaned content with markers removed
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            # Remove leading asterisks and spaces
            line = re.sub(r'^\s*\*\s?', '', line)
            # Skip empty lines at the beginning
            if line or cleaned_lines:
                cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def _parse_types(type_string: str) -> List[str]:
        """
        Parse type string into list of types.
        
        Handles union types like "string|number|null" and complex types.
        
        Args:
            type_string: Type annotation string from JSDoc
            
        Returns:
            List of individual types
        """
        # Split on | for union types, clean up whitespace
        types = [t.strip() for t in type_string.split('|')]
        return [t for t in types if t]  # Filter out empty strings
    
    @staticmethod
    def _extract_description_parts(content: str) -> Optional[Description]:
        """
        Extract description from comment content.
        
        Args:
            content: Cleaned comment content
            
        Returns:
            Description object or None if no description found
        """
        # Find the description (content before first @tag)
        lines = content.split('\n')
        desc_lines = []
        
        for line in lines:
            if line.strip().startswith('@'):
                break
            desc_lines.append(line)
        
        if not desc_lines or not any(line.strip() for line in desc_lines):
            return None
            
        full_desc = '\n'.join(desc_lines).strip()
        if not full_desc:
            return None
            
        # Extract summary (first sentence or first line)
        summary = full_desc.split('.')[0]
        if not summary.endswith('.') and '.' in full_desc:
            summary += '.'
        
        # If no period found, use first line as summary
        if summary == full_desc:
            summary = full_desc.split('\n')[0].strip()
            
        return Description(full=full_desc, summary=summary)
    
    @classmethod
    def _parse_parameters(cls, content: str) -> List[Parameter]:
        """
        Parse @param tags from comment content.
        
        Args:
            content: Comment content to parse
            
        Returns:
            List of Parameter objects
        """
        params = []
        matches = cls.PARAM_PATTERN.findall(content)
        
        for type_str, bracketed_name, name, description in matches:
            # Check if parameter is optional (surrounded by [])
            optional = bracketed_name.startswith('[') and bracketed_name.endswith(']')
            param_name = name if name else bracketed_name.strip('[]')
            
            # Handle default values (e.g., "email=user@example.com" -> "email")
            if '=' in param_name:
                param_name = param_name.split('=')[0]
            
            params.append(Parameter(
                types=cls._parse_types(type_str),
                name=param_name,
                description=description.strip(),
                optional=optional
            ))
        
        return params
    
    @classmethod 
    def _parse_returns(cls, content: str) -> List[ReturnValue]:
        """
        Parse @returns/@return tags from comment content.
        
        Args:
            content: Comment content to parse
            
        Returns:
            List of ReturnValue objects
        """
        returns = []
        matches = cls.RETURN_PATTERN.findall(content)
        
        for type_str, description in matches:
            returns.append(ReturnValue(
                types=cls._parse_types(type_str),
                description=description.strip()
            ))
            
        return returns
    
    @classmethod
    def _parse_properties(cls, content: str) -> List[Property]:
        """
        Parse @property tags from comment content.
        
        Args:
            content: Comment content to parse
            
        Returns:
            List of Property objects
        """
        properties = []
        matches = cls.PROPERTY_PATTERN.findall(content)
        
        for type_str, bracketed_name, name, description in matches:
            # Check if property is optional
            optional = bracketed_name.startswith('[') and bracketed_name.endswith(']')
            prop_name = name if name else bracketed_name.strip('[]')
            
            # Handle default values (e.g., "email=user@example.com" -> "email")
            if '=' in prop_name:
                prop_name = prop_name.split('=')[0]
            
            properties.append(Property(
                types=cls._parse_types(type_str),
                name=prop_name,
                description=description.strip(),
                optional=optional
            ))
            
        return properties
    
    @classmethod
    def _parse_typedefs(cls, content: str) -> List[TypeDef]:
        """
        Parse @typedef tags from comment content.
        
        Args:
            content: Comment content to parse
            
        Returns:
            List of TypeDef objects
        """
        typedefs = []
        matches = cls.TYPEDEF_PATTERN.findall(content)
        
        if not matches:
            return typedefs
        
        # Parse all @property tags to associate with typedefs
        all_properties = cls._parse_properties(content)
        
        # For each typedef, find associated properties
        for type_str, name, description in matches:
            # For now, associate all properties with each typedef
            # TODO: In future, we could improve this to associate properties
            # with their specific typedef based on position in the comment
            typedef_properties = all_properties if len(matches) == 1 else []
            
            typedefs.append(TypeDef(
                types=cls._parse_types(type_str),
                name=name,
                description=description.strip() if description else None,
                properties=typedef_properties
            ))
            
        return typedefs
    
    @classmethod
    def _parse_examples(cls, content: str) -> List[Example]:
        """
        Parse @example tags from comment content.
        
        Args:
            content: Comment content to parse
            
        Returns:
            List of Example objects
        """
        examples = []
        
        # Find all @example blocks including position info
        example_matches = []
        for match in re.finditer(r'@example\s*\n?', content):
            start_pos = match.end()
            example_matches.append(start_pos)
        
        if not example_matches:
            return examples
            
        # For each @example, find its content until next @tag or end
        for i, start_pos in enumerate(example_matches):
            # Find the end position (next @tag or end of content)
            next_tag_match = re.search(r'@\w+', content[start_pos:])
            if next_tag_match:
                end_pos = start_pos + next_tag_match.start()
            else:
                end_pos = len(content)
            
            # Extract example content
            example_content = content[start_pos:end_pos].strip()
            if not example_content:
                continue
                
            # Clean up the example content line by line
            example_lines = example_content.split('\n')
            cleaned_lines = []
            
            for line in example_lines:
                # Remove leading asterisks and spaces but preserve code indentation
                cleaned_line = re.sub(r'^\s*\*\s?', '', line.rstrip())
                cleaned_lines.append(cleaned_line)
            
            # Remove empty lines at start and end
            while cleaned_lines and not cleaned_lines[0]:
                cleaned_lines.pop(0)
            while cleaned_lines and not cleaned_lines[-1]:
                cleaned_lines.pop()
                
            if cleaned_lines:
                examples.append(Example(
                    code='\n'.join(cleaned_lines),
                    description=None  # Could be enhanced to parse description
                ))
        
        return examples
    
    @classmethod
    def _parse_throws(cls, content: str) -> List[Throws]:
        """
        Parse @throws tags from comment content.
        
        Args:
            content: Comment content to parse
            
        Returns:
            List of Throws objects
        """
        throws = []
        matches = cls.THROWS_PATTERN.findall(content)
        
        for type_str, description in matches:
            throws.append(Throws(
                types=cls._parse_types(type_str),
                description=description.strip()
            ))
            
        return throws


def parse(jsdoc_string: str, include_code: bool = True) -> JSDocComment:
    """
    Parse a JSDoc comment string into a structured JSDocComment object.
    
    This is the main public interface for the jsdoc-parser package. It takes
    a JSDoc comment string and returns a structured representation of all
    the tags and content found within it.
    
    Args:
        jsdoc_string: A JSDoc comment string, typically starting with /**
                     and ending with */. Can also include the code that 
                     follows the comment block.
        include_code: Whether to extract and include any JavaScript code
                     that follows the JSDoc comment block
    
    Returns:
        JSDocComment: A structured representation of the parsed JSDoc comment
        
    Raises:
        ValueError: If the input string is not a valid JSDoc comment format
        
    Example:
        >>> jsdoc = '''/**
        ...  * Adds two numbers together.
        ...  * @param {number} a - The first number
        ...  * @param {number} b - The second number
        ...  * @returns {number} The sum of a and b
        ...  * @example
        ...  * add(1, 2); // returns 3
        ...  */
        ... function add(a, b) {
        ...   return a + b;
        ... }'''
        >>> result = parse(jsdoc)
        >>> print(result.description.summary)
        'Adds two numbers together.'
        >>> print(result.params[0].name)
        'a'
        >>> print(result.returns[0].types)
        ['number']
        >>> print(result.code)
        'function add(a, b) {\\n  return a + b;\\n}'
    """
    if not jsdoc_string or not jsdoc_string.strip():
        raise ValueError("JSDoc string cannot be empty")
    
    # Find all comment blocks in the input string
    comment_matches = list(JSDocParser.COMMENT_BLOCK_PATTERN.finditer(jsdoc_string))
    code = None
    
    if not comment_matches:
        # Try to handle comments without /** */ wrapper
        if jsdoc_string.strip().startswith('*'):
            content = jsdoc_string
        else:
            raise ValueError("Invalid JSDoc comment format: must be wrapped in /** */")
    else:
        # Process the first comment block for main content
        first_match = comment_matches[0]
        content = first_match.group(1)
        
        # Extract code that follows the last comment if include_code is True
        if include_code:
            # Code comes after the last comment block
            last_comment_end_pos = comment_matches[-1].end()
            remaining_text = jsdoc_string[last_comment_end_pos:].strip()
            
            if remaining_text:
                code = remaining_text
    
    # Clean the content
    cleaned_content = JSDocParser._clean_comment_content(content)
    
    # Parse all components - find the block with the richest documentation
    description = None
    params = []
    returns = []
    properties = []
    examples = []
    throws = []
    
    if comment_matches:
        # Find the comment block with function documentation (params, returns, etc.)
        main_block_content = None
        for match in comment_matches:
            block_content = JSDocParser._clean_comment_content(match.group(1))
            block_params = JSDocParser._parse_parameters(block_content)
            block_returns = JSDocParser._parse_returns(block_content)
            block_examples = JSDocParser._parse_examples(block_content)
            block_throws = JSDocParser._parse_throws(block_content)
            
            # If this block has function documentation, use it as main
            if block_params or block_returns or block_examples or block_throws:
                main_block_content = block_content
                params = block_params
                returns = block_returns
                examples = block_examples
                throws = block_throws
                break
        
        # If no block has function documentation, use the first block
        if main_block_content is None:
            main_block_content = cleaned_content
        
        # Parse description and properties from the main block
        description = JSDocParser._extract_description_parts(main_block_content)
        properties = JSDocParser._parse_properties(main_block_content)
    else:
        # Single content without /** */ wrapper
        description = JSDocParser._extract_description_parts(cleaned_content)
        params = JSDocParser._parse_parameters(cleaned_content)
        returns = JSDocParser._parse_returns(cleaned_content)
        properties = JSDocParser._parse_properties(cleaned_content)
        examples = JSDocParser._parse_examples(cleaned_content)
        throws = JSDocParser._parse_throws(cleaned_content)
    
    # Parse typedefs from all comment blocks
    typedefs = []
    if comment_matches:
        for match in comment_matches:
            block_content = JSDocParser._clean_comment_content(match.group(1))
            block_typedefs = JSDocParser._parse_typedefs(block_content)
            typedefs.extend(block_typedefs)
    else:
        # Single content without /** */ wrapper
        typedefs = JSDocParser._parse_typedefs(cleaned_content)
    
    return JSDocComment(
        description=description,
        params=params,
        returns=returns,
        typedefs=typedefs,
        properties=properties,
        examples=examples,
        throws=throws,
        code=code,
        raw_comment=jsdoc_string
    )