"""
Comprehensive tests for the JSDoc parser.

This module contains tests for all supported JSDoc tags and parsing functionality.
"""

import pytest
from jsdoc_parser import parse
from jsdoc_parser.models import JSDocComment, Parameter, ReturnValue, TypeDef, Property, Example, Throws, Description


def test_basic_function_comment():
    """Test parsing a basic function with param and return."""
    jsdoc = """/**
     * Adds two numbers together.
     * @param {number} a - The first number
     * @param {number} b - The second number
     * @returns {number} The sum of a and b
     */
    function add(a, b) {
        return a + b;
    }"""
    
    result = parse(jsdoc)
    
    assert result.description is not None
    assert result.description.summary == "Adds two numbers together."
    assert result.description.full == "Adds two numbers together."
    
    assert len(result.params) == 2
    assert result.params[0].name == "a"
    assert result.params[0].types == ["number"]
    assert result.params[0].description == "The first number"
    assert not result.params[0].optional
    
    assert result.params[1].name == "b"
    assert result.params[1].types == ["number"]
    assert result.params[1].description == "The second number"
    
    assert len(result.returns) == 1
    assert result.returns[0].types == ["number"]
    assert result.returns[0].description == "The sum of a and b"
    
    assert result.code.strip().startswith("function add(a, b)")


def test_typedef_with_properties():
    """Test parsing typedef with properties from test.js."""
    jsdoc = """/**
     * @typedef {object} RealEstateListing
     * @property {string|null} url - The URL of the listing.
     * @property {number|null} price - The price of the property.
     * @property {string|null} address - The full address of the property.
     * @property {number|null} beds - The number of bedrooms.
     * @property {number|null} baths - The number of bathrooms.
     * @property {number|null} sqft - The square footage of the property.
     * @property {string|null} imageUrl - The URL of the primary image for the listing.
     * @property {string|null} status - The listing status (e.g., 'OPEN SUN, 2PM TO 4PM', 'LISTED BY REDFIN').
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    assert result.typedef is not None
    assert result.typedef.name == "RealEstateListing"
    assert result.typedef.types == ["object"]
    
    assert len(result.properties) == 8
    
    # Test first property
    url_prop = result.properties[0]
    assert url_prop.name == "url"
    assert url_prop.types == ["string", "null"]
    assert url_prop.description == "The URL of the listing."
    
    # Test another property
    price_prop = result.properties[1]
    assert price_prop.name == "price"
    assert price_prop.types == ["number", "null"]
    assert price_prop.description == "The price of the property."


def test_complex_function_with_example():
    """Test parsing the extractStructuredData function from test.js."""
    jsdoc = """/**
     * Extracts structured data about real estate listings from the page.
     * It iterates through each property card, gathering details like price, address,
     * beds, baths, square footage, image URL, property URL, and listing status.
     *
     * @returns {RealEstateListing[]} An array of objects, where each object represents a single real estate listing.
     *
     * @example
     * // Returns an array of listing objects like this:
     * [
     *   {
     *     "url": "https://www.redfin.com/CA/Roseville/6097-Crater-Lake-Dr-95678/home/19624990",
     *     "price": 799000,
     *     "address": "6097 Crater Lake Dr, Roseville, CA 95678",
     *     "beds": 3,
     *     "baths": 3,
     *     "sqft": 2707,
     *     "imageUrl": "https://ssl.cdn-redfin.com/system_files/media/1109183_JPG/genDesktopMapHomeCardUrl/item_1.jpg",
     *     "status": "REDFIN OPEN SUN, 2PM TO 4PM"
     *   }
     * ]
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    # Test description
    assert result.description is not None
    assert result.description.summary == "Extracts structured data about real estate listings from the page."
    assert "It iterates through each property card" in result.description.full
    
    # Test return value
    assert len(result.returns) == 1
    assert result.returns[0].types == ["RealEstateListing[]"]
    assert "array of objects" in result.returns[0].description
    
    # Test example
    assert len(result.examples) == 1
    example = result.examples[0]
    assert "Returns an array of listing objects" in example.code
    assert '"url": "https://www.redfin.com' in example.code


def test_optional_parameters():
    """Test parsing optional parameters with bracket syntax."""
    jsdoc = """/**
     * Creates a user profile.
     * @param {string} name - User's name
     * @param {number} [age] - User's age (optional)
     * @param {string} [email=user@example.com] - User's email (optional with default)
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    assert len(result.params) == 3
    
    # Required parameter
    assert result.params[0].name == "name"
    assert not result.params[0].optional
    
    # Optional parameter
    assert result.params[1].name == "age"
    assert result.params[1].optional
    
    # Optional parameter with default (should still be marked optional)
    assert result.params[2].name == "email"
    assert result.params[2].optional


def test_throws_tag():
    """Test parsing @throws tags."""
    jsdoc = """/**
     * Validates user input.
     * @param {string} input - The input to validate
     * @throws {Error} If input is invalid
     * @throws {ValidationError} If input fails validation rules
     * @returns {boolean} True if valid
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    assert len(result.throws) == 2
    
    assert result.throws[0].types == ["Error"]
    assert result.throws[0].description == "If input is invalid"
    
    assert result.throws[1].types == ["ValidationError"]
    assert result.throws[1].description == "If input fails validation rules"


def test_union_types():
    """Test parsing union types with pipes."""
    jsdoc = """/**
     * Processes a value that can be multiple types.
     * @param {string|number|boolean} value - The value to process
     * @returns {string|null} Processed value or null
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    # Test parameter union types
    assert len(result.params) == 1
    assert result.params[0].types == ["string", "number", "boolean"]
    
    # Test return union types
    assert len(result.returns) == 1
    assert result.returns[0].types == ["string", "null"]


def test_multiple_examples():
    """Test parsing multiple @example tags."""
    jsdoc = """/**
     * A utility function.
     * @example
     * // Basic usage
     * doSomething(123);
     * 
     * @example
     * // Advanced usage
     * doSomething(456, {option: true});
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    assert len(result.examples) == 2
    assert "Basic usage" in result.examples[0].code
    assert "doSomething(123)" in result.examples[0].code
    assert "Advanced usage" in result.examples[1].code
    assert "doSomething(456" in result.examples[1].code


def test_empty_comment():
    """Test error handling for empty comments."""
    with pytest.raises(ValueError, match="JSDoc string cannot be empty"):
        parse("")
    
    with pytest.raises(ValueError, match="JSDoc string cannot be empty"):
        parse("   ")


def test_invalid_comment_format():
    """Test error handling for invalid comment format."""
    with pytest.raises(ValueError, match="Invalid JSDoc comment format"):
        parse("This is not a JSDoc comment")


def test_comment_without_code():
    """Test parsing comment block without following code."""
    jsdoc = """/**
     * Just a comment with no code following.
     * @param {string} test - A test parameter
     */"""
    
    result = parse(jsdoc)
    
    assert result.description.summary == "Just a comment with no code following."
    assert len(result.params) == 1
    assert result.code is None


def test_include_code_false():
    """Test parsing with include_code=False."""
    jsdoc = """/**
     * A function comment.
     */
    function test() {
        return true;
    }"""
    
    result = parse(jsdoc, include_code=False)
    
    assert result.description.summary == "A function comment."
    assert result.code is None


def test_multiline_description():
    """Test parsing multiline descriptions."""
    jsdoc = """/**
     * This is a long description that spans multiple lines.
     * It provides detailed information about the function.
     * And continues with more details.
     * 
     * @param {string} input - The input parameter
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    assert result.description.summary == "This is a long description that spans multiple lines."
    expected_full = ("This is a long description that spans multiple lines.\n"
                    "It provides detailed information about the function.\n"
                    "And continues with more details.")
    assert result.description.full == expected_full


def test_return_vs_returns():
    """Test that both @return and @returns work."""
    jsdoc1 = """/**
     * @returns {number} A number
     */"""
    
    jsdoc2 = """/**
     * @return {string} A string
     */"""
    
    result1 = parse(jsdoc1, include_code=False)
    result2 = parse(jsdoc2, include_code=False)
    
    assert len(result1.returns) == 1
    assert result1.returns[0].types == ["number"]
    
    assert len(result2.returns) == 1
    assert result2.returns[0].types == ["string"]


def test_preserve_raw_comment():
    """Test that raw comment is preserved."""
    jsdoc = """/**
     * Original comment.
     * @param {string} test - Test param
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    assert result.raw_comment == jsdoc


def test_standard_jsdoc_format():
    """Test parsing standard JSDoc format with short and long descriptions."""
    jsdoc = """/**
     * Validates user input data.
     *
     * This function performs comprehensive validation on user input,
     * checking for required fields, data types, and business rules.
     * It returns detailed error information if validation fails.
     *
     * @param {Object} userData - The user data object to validate
     * @param {Object} [options] - Optional validation configuration
     * @returns {ValidationResult} Result object with success status and errors
     * @throws {ValidationError} When validation configuration is invalid
     */
    function validateUserData(userData, options = {}) {
        // Validation logic here
        return { isValid: true, errors: [] };
    }"""
    
    result = parse(jsdoc)
    
    # Test description parsing with short and long descriptions
    assert result.description is not None
    assert result.description.summary == "Validates user input data."
    
    expected_full = ("Validates user input data.\n\n"
                    "This function performs comprehensive validation on user input,\n"
                    "checking for required fields, data types, and business rules.\n"
                    "It returns detailed error information if validation fails.")
    assert result.description.full == expected_full
    
    # Test parameters
    assert len(result.params) == 2
    
    # Required parameter
    assert result.params[0].name == "userData"
    assert result.params[0].types == ["Object"]
    assert result.params[0].description == "The user data object to validate"
    assert not result.params[0].optional
    
    # Optional parameter
    assert result.params[1].name == "options"
    assert result.params[1].types == ["Object"]
    assert result.params[1].description == "Optional validation configuration"
    assert result.params[1].optional
    
    # Test return
    assert len(result.returns) == 1
    assert result.returns[0].types == ["ValidationResult"]
    assert result.returns[0].description == "Result object with success status and errors"
    
    # Test throws
    assert len(result.throws) == 1
    assert result.throws[0].types == ["ValidationError"]
    assert result.throws[0].description == "When validation configuration is invalid"
    
    # Test code extraction
    assert result.code is not None
    assert "function validateUserData" in result.code


def test_description_only_format():
    """Test parsing JSDoc with only short and long descriptions, no tags."""
    jsdoc = """/**
     * Calculates the total price including tax.
     *
     * This utility function takes a base price and applies the appropriate
     * tax rate based on the customer's location and product category.
     * The calculation includes handling for tax-exempt items and special
     * promotional discounts that may be applied.
     */
    function calculateTotalPrice(basePrice, taxRate, location) {
        return basePrice * (1 + taxRate);
    }"""
    
    result = parse(jsdoc)
    
    # Test description parsing
    assert result.description is not None
    assert result.description.summary == "Calculates the total price including tax."
    
    expected_full = ("Calculates the total price including tax.\n\n"
                    "This utility function takes a base price and applies the appropriate\n"
                    "tax rate based on the customer's location and product category.\n"
                    "The calculation includes handling for tax-exempt items and special\n"
                    "promotional discounts that may be applied.")
    assert result.description.full == expected_full
    
    # Test that no tags were parsed since there are none
    assert len(result.params) == 0
    assert len(result.returns) == 0
    assert len(result.throws) == 0
    assert len(result.examples) == 0
    assert len(result.properties) == 0
    assert result.typedef is None
    
    # Test code extraction
    assert result.code is not None
    assert "function calculateTotalPrice" in result.code
    
    # Test raw comment preservation
    assert result.raw_comment == jsdoc