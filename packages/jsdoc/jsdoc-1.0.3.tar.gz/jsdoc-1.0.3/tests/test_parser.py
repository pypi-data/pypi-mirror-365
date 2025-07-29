"""
Comprehensive tests for the JSDoc parser.

This module contains tests for all supported JSDoc tags and parsing functionality.
"""

import pytest
from jsdoc import parse


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
    
    assert len(result.typedefs) == 1
    assert result.typedefs[0].name == "RealEstateListing"
    assert result.typedefs[0].types == ["object"]
    
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
    assert len(result.typedefs) == 0
    
    # Test code extraction
    assert result.code is not None
    assert "function calculateTotalPrice" in result.code
    
    # Test raw comment preservation
    assert result.raw_comment == jsdoc


def test_typedef_and_function_comment_blocks():
    """Test parsing input with two comment blocks: typedef block followed by function JSDoc."""
    jsdoc_with_two_blocks = """/**
     * @typedef {object} UserProfile
     * @property {string} id - The unique user identifier
     * @property {string} name - The user's full name
     * @property {string|null} email - The user's email address
     * @property {number} age - The user's age in years
     * @property {boolean} isActive - Whether the user account is active
     */

    /**
     * Creates a new user profile with validation.
     * 
     * This function validates user input and creates a properly structured
     * user profile object that conforms to the UserProfile typedef.
     *
     * @param {string} name - The user's full name
     * @param {string} email - The user's email address
     * @param {number} age - The user's age in years
     * @returns {UserProfile} A validated user profile object
     * @throws {ValidationError} If the input data is invalid
     * 
     * @example
     * // Create a new user profile
     * const profile = createUserProfile('John Doe', 'john.doe.email.com', 30);
     * console.log(profile.id); // Generated UUID
     */
    function createUserProfile(name, email, age) {
        if (!name || typeof name !== 'string') {
            throw new ValidationError('Name must be a non-empty string');
        }
        
        const profile = {
            id: generateUUID(),
            name: name.trim(),
            email: email || null,
            age: age,
            isActive: true
        };
        
        return profile;
    }"""
    
    # Parse the first comment block (typedef)
    typedef_result = parse(jsdoc_with_two_blocks)
    
    # Test typedef parsing
    assert len(typedef_result.typedefs) == 1
    assert typedef_result.typedefs[0].name == "UserProfile"
    assert typedef_result.typedefs[0].types == ["object"]
    
    # Test typedef properties (properties are now in the typedef itself, not in the main properties list)  
    assert len(typedef_result.typedefs[0].properties) == 5
    
    # Test specific properties from the typedef
    id_prop = typedef_result.typedefs[0].properties[0]
    assert id_prop.name == "id"
    assert id_prop.types == ["string"]
    assert id_prop.description == "The unique user identifier"
    assert not id_prop.optional
    
    email_prop = typedef_result.typedefs[0].properties[2]
    assert email_prop.name == "email"
    assert email_prop.types == ["string", "null"]
    assert email_prop.description == "The user's email address"
    
    isActive_prop = typedef_result.typedefs[0].properties[4]
    assert isActive_prop.name == "isActive"
    assert isActive_prop.types == ["boolean"]
    assert isActive_prop.description == "Whether the user account is active"
    
    # Since the parser currently processes only the first comment block,
    # we need to test the function comment separately
    function_jsdoc = """/**
     * Creates a new user profile with validation.
     * 
     * This function validates user input and creates a properly structured
     * user profile object that conforms to the UserProfile typedef.
     *
     * @param {string} name - The user's full name
     * @param {string} email - The user's email address
     * @param {number} age - The user's age in years
     * @returns {UserProfile} A validated user profile object
     * @throws {ValidationError} If the input data is invalid
     * 
     * @example
     * // Create a new user profile
     * const profile = createUserProfile('John Doe', 'john.doe.email.com', 30);
     * console.log(profile.id); // Generated UUID
     */
    function createUserProfile(name, email, age) {
        if (!name || typeof name !== 'string') {
            throw new ValidationError('Name must be a non-empty string');
        }
        
        const profile = {
            id: generateUUID(),
            name: name.trim(),
            email: email || null,
            age: age,
            isActive: true
        };
        
        return profile;
    }"""
    
    function_result = parse(function_jsdoc)
    
    # Test function description
    assert function_result.description is not None
    assert function_result.description.summary == "Creates a new user profile with validation."
    expected_full = ("Creates a new user profile with validation.\n\n"
                    "This function validates user input and creates a properly structured\n"
                    "user profile object that conforms to the UserProfile typedef.")
    assert function_result.description.full == expected_full
    
    # Test function parameters
    assert len(function_result.params) == 3
    
    name_param = function_result.params[0]
    assert name_param.name == "name"
    assert name_param.types == ["string"]
    assert name_param.description == "The user's full name"
    assert not name_param.optional
    
    email_param = function_result.params[1]
    assert email_param.name == "email"
    assert email_param.types == ["string"]
    assert email_param.description == "The user's email address"
    
    age_param = function_result.params[2]
    assert age_param.name == "age"
    assert age_param.types == ["number"]
    assert age_param.description == "The user's age in years"
    
    # Test return value
    assert len(function_result.returns) == 1
    assert function_result.returns[0].types == ["UserProfile"]
    assert function_result.returns[0].description == "A validated user profile object"
    
    # Test throws
    assert len(function_result.throws) == 1
    assert function_result.throws[0].types == ["ValidationError"]
    assert function_result.throws[0].description == "If the input data is invalid"
    
    # Test example
    assert len(function_result.examples) == 1
    example = function_result.examples[0]
    assert "Create a new user profile" in example.code
    assert "createUserProfile('John Doe', 'john.doe.email.com', 30)" in example.code
    assert "console.log(profile.id)" in example.code
    
    # Test code extraction - this is crucial for verifying "code" is properly parsed
    assert function_result.code is not None
    assert "function createUserProfile(name, email, age)" in function_result.code
    assert "if (!name || typeof name !== 'string')" in function_result.code
    assert "throw new ValidationError" in function_result.code
    assert "generateUUID()" in function_result.code
    assert "return profile;" in function_result.code
    
    # Verify the function code contains the complete implementation
    lines_in_code = function_result.code.split('\n')
    assert len(lines_in_code) > 10  # Should have multiple lines of actual function code
    
    # With the new parser logic, the result now includes function documentation
    # from the richest comment block AND typedefs from all blocks
    assert len(typedef_result.params) == 3  # Function parameters from second block
    assert len(typedef_result.returns) == 1  # Function return from second block  
    assert len(typedef_result.throws) == 1   # Function throws from second block
    assert len(typedef_result.examples) == 1 # Function examples from second block


def test_multiple_typedefs_single_block():
    """Test parsing multiple typedef definitions in a single comment block."""
    jsdoc = """/**
     * @typedef {object} User
     * @property {string} id - User identifier
     * @property {string} name - User name
     * 
     * @typedef {object} Role
     * @property {string} name - Role name
     * @property {string[]} permissions - Role permissions
     * 
     * @typedef {string} Status - User status (active, inactive, pending)
     */"""
    
    result = parse(jsdoc, include_code=False)
    
    # Test that we have 3 typedefs
    assert len(result.typedefs) == 3
    
    # Test first typedef (User)
    user_typedef = result.typedefs[0]
    assert user_typedef.name == "User"
    assert user_typedef.types == ["object"]
    assert user_typedef.description is None
    
    # Test second typedef (Role)
    role_typedef = result.typedefs[1]
    assert role_typedef.name == "Role"
    assert role_typedef.types == ["object"]
    assert role_typedef.description is None
    
    # Test third typedef (Status)
    status_typedef = result.typedefs[2]
    assert status_typedef.name == "Status"
    assert status_typedef.types == ["string"]
    assert status_typedef.description == "User status (active, inactive, pending)"
    
    # Test properties - currently all properties are associated with all typedefs when multiple exist
    # This could be improved in future to associate properties with their specific typedef
    assert len(result.properties) == 4  # 2 from User + 2 from Role


def test_multiple_typedefs_separate_blocks():
    """Test parsing multiple typedef definitions in separate comment blocks."""
    jsdoc_multiple_blocks = """/**
     * @typedef {object} Product
     * @property {string} id - Product identifier
     * @property {string} name - Product name
     * @property {number} price - Product price
     */

    /**
     * @typedef {object} Category
     * @property {string} id - Category identifier  
     * @property {string} name - Category name
     * @property {Product[]} products - Products in this category
     */

    /**
     * @typedef {object} Store
     * @property {string} name - Store name
     * @property {Category[]} categories - Store categories
     */

    function getStore() {
        return storeData;
    }"""
    
    result = parse(jsdoc_multiple_blocks)
    
    # Test that we have 3 typedefs from separate blocks
    assert len(result.typedefs) == 3
    
    # Test first typedef (Product)
    product_typedef = result.typedefs[0]
    assert product_typedef.name == "Product"
    assert product_typedef.types == ["object"]
    assert len(product_typedef.properties) == 3
    assert product_typedef.properties[0].name == "id"
    assert product_typedef.properties[1].name == "name"
    assert product_typedef.properties[2].name == "price"
    
    # Test second typedef (Category)
    category_typedef = result.typedefs[1]
    assert category_typedef.name == "Category"
    assert category_typedef.types == ["object"]
    assert len(category_typedef.properties) == 3
    assert category_typedef.properties[0].name == "id"
    assert category_typedef.properties[1].name == "name"
    assert category_typedef.properties[2].name == "products"
    assert category_typedef.properties[2].types == ["Product[]"]
    
    # Test third typedef (Store)
    store_typedef = result.typedefs[2]
    assert store_typedef.name == "Store"
    assert store_typedef.types == ["object"]
    assert len(store_typedef.properties) == 2
    assert store_typedef.properties[0].name == "name"
    assert store_typedef.properties[1].name == "categories"
    assert store_typedef.properties[1].types == ["Category[]"]
    
    # Test that code is properly extracted after all typedef blocks
    assert result.code is not None
    assert "function getStore()" in result.code
    assert "return storeData;" in result.code
    
    # Test function name extraction
    assert result.function_name == "getStore"
    
    # Test that main comment block (first one) doesn't have other JSDoc elements
    assert result.description is None
    assert len(result.params) == 0
    assert len(result.returns) == 0


def test_mixed_typedef_and_function_documentation():
    """Test parsing typedefs mixed with function documentation."""
    jsdoc_mixed = """/**
     * @typedef {object} Config
     * @property {string} apiUrl - API base URL
     * @property {boolean} debug - Debug mode flag
     */

    /**
     * Initializes the application with given configuration.
     * 
     * This function sets up the application using the provided configuration
     * object and returns a promise that resolves when initialization is complete.
     *
     * @param {Config} config - Configuration object
     * @param {object} [options] - Optional settings
     * @returns {Promise<void>} Promise that resolves when initialized
     * @throws {ConfigError} If configuration is invalid
     * 
     * @example
     * // Initialize with configuration
     * await initializeApp({
     *   apiUrl: 'https://api.example.com',
     *   debug: false
     * });
     */
    async function initializeApp(config, options = {}) {
        validateConfig(config);
        await setupDatabase(config);
        await loadPlugins(options);
    }"""
    
    result = parse(jsdoc_mixed)
    
    # Test typedef from first block
    assert len(result.typedefs) == 1
    config_typedef = result.typedefs[0]
    assert config_typedef.name == "Config"
    assert config_typedef.types == ["object"]
    assert len(config_typedef.properties) == 2
    assert config_typedef.properties[0].name == "apiUrl"
    assert config_typedef.properties[1].name == "debug"
    
    # Test function documentation from second block (first block content)
    assert result.description is not None
    assert result.description.summary == "Initializes the application with given configuration."
    assert "This function sets up the application" in result.description.full
    
    # Test function parameters
    assert len(result.params) == 2
    assert result.params[0].name == "config"
    assert result.params[0].types == ["Config"]
    assert result.params[1].name == "options"
    assert result.params[1].optional
    
    # Test function return
    assert len(result.returns) == 1
    assert result.returns[0].types == ["Promise<void>"]
    
    # Test function throws
    assert len(result.throws) == 1
    assert result.throws[0].types == ["ConfigError"]
    
    # Test function example
    assert len(result.examples) == 1
    assert "Initialize with configuration" in result.examples[0].code
    assert "initializeApp({" in result.examples[0].code
    
    # Test code extraction
    assert result.code is not None
    assert "async function initializeApp" in result.code
    assert "validateConfig(config)" in result.code
    assert "await setupDatabase(config)" in result.code
    
    # Test function name extraction
    assert result.function_name == "initializeApp"


def test_function_name_extraction():
    """Test function name extraction from various JavaScript function definitions."""
    
    # Test 1: Standard function declaration
    jsdoc1 = """/**
     * Test function.
     */
    function testFunction() {
        return true;
    }"""
    result1 = parse(jsdoc1)
    assert result1.function_name == "testFunction"
    
    # Test 2: Async function declaration
    jsdoc2 = """/**
     * Async test function.
     */
    async function asyncTestFunction() {
        return await something();
    }"""
    result2 = parse(jsdoc2)
    assert result2.function_name == "asyncTestFunction"
    
    # Test 3: Export function declaration
    jsdoc3 = """/**
     * Exported function.
     */
    export function exportedFunction() {
        return data;
    }"""
    result3 = parse(jsdoc3)
    assert result3.function_name == "exportedFunction"
    
    # Test 4: Export async function declaration
    jsdoc4 = """/**
     * Exported async function.
     */
    export async function exportedAsyncFunction() {
        return await data;
    }"""
    result4 = parse(jsdoc4)
    assert result4.function_name == "exportedAsyncFunction"
    
    # Test 5: Const arrow function
    jsdoc5 = """/**
     * Arrow function.
     */
    const arrowFunction = () => {
        return 42;
    }"""
    result5 = parse(jsdoc5)
    assert result5.function_name == "arrowFunction"
    
    # Test 6: Const async arrow function
    jsdoc6 = """/**
     * Async arrow function.
     */
    const asyncArrowFunction = async () => {
        return await getValue();
    }"""
    result6 = parse(jsdoc6)
    assert result6.function_name == "asyncArrowFunction"
    
    # Test 7: Const function expression
    jsdoc7 = """/**
     * Function expression.
     */
    const functionExpression = function() {
        return "hello";
    }"""
    result7 = parse(jsdoc7)
    assert result7.function_name == "functionExpression"
    
    # Test 8: Const async function expression
    jsdoc8 = """/**
     * Async function expression.
     */
    const asyncFunctionExpression = async function() {
        return await "hello";
    }"""
    result8 = parse(jsdoc8)
    assert result8.function_name == "asyncFunctionExpression"
    
    # Test 9: Object method shorthand
    jsdoc9 = """/**
     * Object method.
     */
    methodName() {
        return this.value;
    }"""
    result9 = parse(jsdoc9)
    assert result9.function_name == "methodName"
    
    # Test 10: Async object method shorthand
    jsdoc10 = """/**
     * Async object method.
     */
    async asyncMethodName() {
        return await this.value;
    }"""
    result10 = parse(jsdoc10)
    assert result10.function_name == "asyncMethodName"
    
    # Test 11: Object method with function keyword
    jsdoc11 = """/**
     * Object method with function keyword.
     */
    methodWithFunction: function() {
        return this.data;
    }"""
    result11 = parse(jsdoc11)
    assert result11.function_name == "methodWithFunction"
    
    # Test 12: Object method with async function keyword
    jsdoc12 = """/**
     * Async object method with function keyword.
     */
    asyncMethodWithFunction: async function() {
        return await this.data;
    }"""
    result12 = parse(jsdoc12)
    assert result12.function_name == "asyncMethodWithFunction"
    
    # Test 13: Class method
    jsdoc13 = """/**
     * Class method.
     */
    classMethod() {
        return this.property;
    }"""
    result13 = parse(jsdoc13)
    assert result13.function_name == "classMethod"
    
    # Test 14: Static class method
    jsdoc14 = """/**
     * Static class method.
     */
    static staticMethod() {
        return SomeClass.value;
    }"""
    result14 = parse(jsdoc14)
    assert result14.function_name == "staticMethod"
    
    # Test 15: Let variable arrow function
    jsdoc15 = """/**
     * Let arrow function.
     */
    let letArrowFunction = (param) => {
        return param * 2;
    }"""
    result15 = parse(jsdoc15)
    assert result15.function_name == "letArrowFunction"
    
    # Test 16: Var variable function expression
    jsdoc16 = """/**
     * Var function expression.
     */
    var varFunctionExpression = function(a, b) {
        return a + b;
    }"""
    result16 = parse(jsdoc16)
    assert result16.function_name == "varFunctionExpression"


def test_function_name_extraction_edge_cases():
    """Test edge cases for function name extraction."""
    
    # Test 1: No code following JSDoc
    jsdoc1 = """/**
     * Just a comment.
     */"""
    result1 = parse(jsdoc1, include_code=False)
    assert result1.function_name is None
    
    # Test 2: Code without function
    jsdoc2 = """/**
     * Variable declaration.
     */
    const someVariable = "value";"""
    result2 = parse(jsdoc2)
    assert result2.function_name is None
    
    # Test 3: Multi-line function definition
    jsdoc3 = """/**
     * Multi-line function.
     */
    function multiLineFunction(
        param1,
        param2,
        param3
    ) {
        return param1 + param2 + param3;
    }"""
    result3 = parse(jsdoc3)
    assert result3.function_name == "multiLineFunction"
    
    # Test 4: Function with complex parameters
    jsdoc4 = """/**
     * Function with complex parameters.
     */
    function complexParams({ name, age = 25 }, ...rest) {
        return { name, age, rest };
    }"""
    result4 = parse(jsdoc4)
    assert result4.function_name == "complexParams"
    
    # Test 5: Arrow function with parameters
    jsdoc5 = """/**
     * Arrow function with parameters.
     */
    const arrowWithParams = (a, b, c) => {
        return a + b + c;
    }"""
    result5 = parse(jsdoc5)
    assert result5.function_name == "arrowWithParams"
    
    # Test 6: Single-line arrow function
    jsdoc6 = """/**
     * Single-line arrow function.
     */
    const singleLineArrow = x => x * 2;"""
    result6 = parse(jsdoc6)
    assert result6.function_name == "singleLineArrow"


def test_function_name_with_existing_tests():
    """Test that function names are extracted in existing test cases."""
    
    # Test basic function comment (existing test)
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
    assert result.function_name == "add"
    assert result.code.strip().startswith("function add(a, b)")
    
    # Test description only format (existing test)  
    jsdoc2 = """/**
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
    
    result2 = parse(jsdoc2)
    assert result2.function_name == "calculateTotalPrice"
    assert "function calculateTotalPrice" in result2.code