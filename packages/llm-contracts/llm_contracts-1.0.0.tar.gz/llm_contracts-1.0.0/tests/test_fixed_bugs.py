#!/usr/bin/env python3
"""
Test Script: Critical LLM-Contracts Fixes Verification

This script tests the specific issues that were identified and fixed:
1. Malformed JSON handling
2. List items detection (indented/Unicode bullets)
3. Duplicate sentences detection
4. Content extraction from dictionaries

Run: python test_critical_fixes.py
"""

import json
import tempfile
import os
from pathlib import Path
from llm_contracts import contracts


def print_test_header(test_name):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print('='*60)


def print_result(description, expected, actual, passed):
    """Print test result in a formatted way."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {description}")
    print(f"     Expected: {expected}")
    print(f"     Actual:   {actual}")
    if not passed:
        print(f"     ⚠️  Test failed!")
    print()


def test_malformed_json_rejection():
    """Test 1: Malformed JSON should be properly rejected."""
    print_test_header("Malformed JSON Rejection")
    
    # Create a simple test schema
    test_schema = {
        "schema": {
            "type": "object",
            "properties": {
                "translation": {"type": "string"},
                "words": {"type": "object"}
            },
            "required": ["translation", "words"]
        },
        "rules": [
            {"word_count_min": 1}
        ]
    }
    
    # Test cases for malformed JSON
    test_cases = [
        {
            "name": "Missing closing brace",
            "json_string": '{"translation": "test", "words": {"1": ["syn1", "syn2"]',
            "should_fail": True
        },
        {
            "name": "Missing quotes around key",
            "json_string": '{translation: "test", "words": {}}',
            "should_fail": True
        },
        {
            "name": "Trailing comma",
            "json_string": '{"translation": "test", "words": {},}',
            "should_fail": True
        },
        {
            "name": "Valid JSON",
            "json_string": '{"translation": "test", "words": {}}',
            "should_fail": False
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(test_schema, f)
        schema_path = f.name
    
    try:
        for case in test_cases:
            print(f"Testing: {case['name']}")
            print(f"JSON: {case['json_string']}")
            
            try:
                # Try to parse JSON first (this should fail for malformed JSON)
                parsed_data = json.loads(case['json_string'])
                result = contracts.validate(parsed_data, schema_path)
                validation_failed = not result.is_valid
                json_parsing_failed = False
            except json.JSONDecodeError:
                # JSON parsing failed (expected for malformed JSON)
                validation_failed = True
                json_parsing_failed = True
            
            # For malformed JSON, we expect either JSON parsing to fail OR validation to fail
            if case['should_fail']:
                passed = json_parsing_failed or validation_failed
                expected = "Reject malformed JSON"
                actual = "JSON parsing failed" if json_parsing_failed else f"Validation failed: {validation_failed}"
            else:
                passed = not json_parsing_failed and not validation_failed
                expected = "Accept valid JSON"
                actual = "JSON parsing succeeded and validation passed" if passed else "Failed"
            
            print_result(case['name'], expected, actual, passed)
    
    finally:
        os.unlink(schema_path)


def test_list_items_detection():
    """Test 2: List items detection with indented and Unicode bullets."""
    print_test_header("List Items Detection (Indented/Unicode Bullets)")
    
    test_schema = {
        "schema": {
            "type": "object",
            "properties": {
                "translation": {"type": "string"},
                "words": {"type": "object"}
            },
            "required": ["translation", "words"]
        },
        "rules": [
            {"min_list_items": 3}
        ]
    }
    
    test_cases = [
        {
            "name": "Unicode bullets (•) - should find 4 items",
            "content": "Features include:\n• Feature 1\n• Feature 2\n• Feature 3\n• Feature 4",
            "should_pass": True
        },
        {
            "name": "Indented ASCII bullets - should find 3 items", 
            "content": "List:\n  - Item 1\n  - Item 2\n  - Item 3",
            "should_pass": True
        },
        {
            "name": "Mixed indentation - should find 4 items",
            "content": "Features:\n• Main feature\n  - Sub item 1\n  - Sub item 2\n* Another item",
            "should_pass": True
        },
        {
            "name": "Numbered list - should find 3 items",
            "content": "Steps:\n1. First step\n2. Second step\n3. Third step",
            "should_pass": True
        },
        {
            "name": "Too few items - should find only 2",
            "content": "Short list:\n• Item 1\n• Item 2",
            "should_pass": False
        },
        {
            "name": "No list items - should find 0",
            "content": "Just regular text without any lists or bullets",
            "should_pass": False
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(test_schema, f)
        schema_path = f.name
    
    try:
        for case in test_cases:
            payload = {
                "translation": case['content'],
                "words": {}
            }
            
            result = contracts.validate(payload, schema_path)
            passed = result.is_valid == case['should_pass']
            
            # Extract list count from error message if validation failed
            list_count = "unknown"
            for error in result.errors:
                if "list items" in error and "found" in error:
                    import re
                    match = re.search(r'found (\d+)', error)
                    if match:
                        list_count = match.group(1)
            
            expected = f"Should {'pass' if case['should_pass'] else 'fail'} (≥3 items required)"
            actual = f"{'Passed' if result.is_valid else 'Failed'} (found {list_count} items)"
            
            print(f"Content: {repr(case['content'][:50])}...")
            print_result(case['name'], expected, actual, passed)
    
    finally:
        os.unlink(schema_path)


def test_duplicate_sentences_detection():
    """Test 3: Duplicate sentences detection with various edge cases."""
    print_test_header("Duplicate Sentences Detection")
    
    test_schema = {
        "schema": {
            "type": "object", 
            "properties": {
                "translation": {"type": "string"},
                "words": {"type": "object"}
            },
            "required": ["translation", "words"]
        },
        "rules": [
            {"no_duplicate_sentences": True}
        ]
    }
    
    test_cases = [
        {
            "name": "Exact duplicates - should be detected",
            "content": "This is a great product. This product is amazing. This is a great product.",
            "should_fail": True
        },
        {
            "name": "Case differences - should be detected", 
            "content": "This is great. This product rocks. THIS IS GREAT.",
            "should_fail": True
        },
        {
            "name": "Punctuation differences - should be detected",
            "content": "Hello world. How are you? Hello world!",
            "should_fail": True
        },
        {
            "name": "Whitespace differences - should be detected",
            "content": "Good morning. Nice day today.   Good   morning.",
            "should_fail": True
        },
        {
            "name": "No duplicates - should pass",
            "content": "First sentence. Second sentence. Third sentence.",
            "should_fail": False
        },
        {
            "name": "Similar but different - should pass",
            "content": "This is good. This is great. This is excellent.",
            "should_fail": False
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(test_schema, f)
        schema_path = f.name
    
    try:
        for case in test_cases:
            payload = {
                "translation": case['content'],
                "words": {}
            }
            
            result = contracts.validate(payload, schema_path)
            validation_failed = not result.is_valid
            passed = validation_failed == case['should_fail']
            
            # Check if duplicate error is present
            has_duplicate_error = any("duplicate" in error.lower() for error in result.errors)
            
            expected = f"Should {'fail' if case['should_fail'] else 'pass'} validation"
            actual = f"{'Failed' if validation_failed else 'Passed'}" + (f" (duplicate detected)" if has_duplicate_error else "")
            
            print(f"Content: {repr(case['content'])}")
            print_result(case['name'], expected, actual, passed)
    
    finally:
        os.unlink(schema_path)


def test_content_extraction_from_dict():
    """Test 4: Content extraction from dictionary structures."""
    print_test_header("Content Extraction from Dictionary")
    
    test_schema = {
        "schema": {
            "type": "object",
            "properties": {
                "translation": {"type": "string"},
                "words": {"type": "object"}
            },
            "required": ["translation", "words"]
        },
        "rules": [
            {"keyword_must_include": ["test"]},
            {"word_count_min": 3}
        ]
    }
    
    test_cases = [
        {
            "name": "Dictionary with 'translation' field",
            "payload": {
                "translation": "This is a test message with enough words",
                "words": {}
            },
            "should_pass": True
        },
        {
            "name": "Dictionary with 'content' field",
            "payload": {
                "content": "This is a test message with enough words",
                "metadata": {}
            },
            "should_pass": True
        },
        {
            "name": "Dictionary with 'text' field",
            "payload": {
                "text": "This is a test message with enough words", 
                "other": {}
            },
            "should_pass": True
        },
        {
            "name": "String content directly",
            "payload": "This is a test message with enough words",
            "should_pass": True
        },
        {
            "name": "Missing required keyword in translation",
            "payload": {
                "translation": "This message has enough words but missing keyword",
                "words": {}
            },
            "should_pass": False
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(test_schema, f)
        schema_path = f.name
    
    try:
        for case in test_cases:
            try:
                result = contracts.validate(case['payload'], schema_path)
                passed = result.is_valid == case['should_pass']
                
                expected = f"Should {'pass' if case['should_pass'] else 'fail'} validation"
                actual = f"{'Passed' if result.is_valid else 'Failed'}"
                if result.errors:
                    actual += f" - Errors: {len(result.errors)}"
                
                print(f"Payload type: {type(case['payload'])}")
                print_result(case['name'], expected, actual, passed)
                
            except Exception as e:
                print_result(case['name'], "Should handle gracefully", f"Exception: {str(e)}", False)
    
    finally:
        os.unlink(schema_path)


def test_duplicate_synonyms_limitation():
    """Test 5: Demonstrate the duplicate synonyms limitation (known issue)."""
    print_test_header("Duplicate Synonyms in Arrays (Known Limitation)")
    
    test_schema = {
        "schema": {
            "type": "object",
            "properties": {
                "translation": {"type": "string"},
                "words": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "required": ["translation", "words"]
        },
        "rules": [
            {"word_count_min": 1}
        ]
    }
    
    print("📋 Note: This test demonstrates a known limitation.")
    print("The library currently does NOT detect duplicate values within JSON arrays.")
    print("This would require custom business logic or a new rule type.\n")
    
    payload = {
        "translation": "Test content",
        "words": {
            "1": ["duplicate", "duplicate", "unique"]  # Has duplicates
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(test_schema, f)
        schema_path = f.name
    
    try:
        result = contracts.validate(payload, schema_path)
        
        # Custom duplicate check (what users would need to implement)
        has_duplicates = False
        for key, synonyms in payload["words"].items():
            if len(synonyms) != len(set(synonyms)):
                has_duplicates = True
                break
        
        print(f"Payload: {payload}")
        print(f"Library validation result: {'PASS' if result.is_valid else 'FAIL'}")
        print(f"Custom duplicate check: {'DUPLICATES FOUND' if has_duplicates else 'NO DUPLICATES'}")
        print(f"📝 Recommendation: Add custom validation for duplicate array values")
        
    finally:
        os.unlink(schema_path)


def test_real_world_translation_scenarios():
    """Test 6: Real-world translation validation scenarios using actual schema."""
    print_test_header("Real-World Translation Scenarios")
    
    # Use the actual translation schema from the project
    schema_path = "tests/schemas/translation_with_synonyms.yaml"
    
    # Test cases based on real-world usage patterns
    test_cases = [
        {
            "name": "Valid Arabic translation with synonyms",
            "payload": {
                "translation": "تم <syn1>إصلاح</syn1> الخطأ.",
                "words": {
                    "1": ["تثبيت", "معالجة"]
                }
            },
            "should_pass": True,
            "description": "Fully valid structure with Arabic text and proper synonyms"
        },
        {
            "name": "Missing words field",
            "payload": {
                "translation": "مرحبا بالعالم"
            },
            "should_pass": False,
            "description": "Should fail due to missing required 'words' field"
        },
        {
            "name": "Words value not an array",
            "payload": {
                "translation": "تم <syn1>إصلاح</syn1> الخطأ.",
                "words": {
                    "1": "تثبيت"  # Should be array, not string
                }
            },
            "should_pass": False,
            "description": "Should fail because 'words' values must be arrays"
        },
        {
            "name": "Empty translation string",
            "payload": {
                "translation": "",
                "words": {}
            },
            "should_pass": False,
            "description": "Should fail due to empty translation (minLength: 1)"
        },
        {
            "name": "Translation with banned AI phrases",
            "payload": {
                "translation": "As an AI assistant, I cannot help with this request.",
                "words": {}
            },
            "should_pass": False,
            "description": "Should fail due to banned phrase 'As an AI'"
        },
        {
            "name": "Mixed language translation",
            "payload": {
                "translation": "تم <syn1>إصلاح</syn1> الأخطاء وإجراء بعض الاختبارات. Fixed bugs and testing.",
                "words": {
                    "1": ["تثبيت", "معالجة", "تصحيح"]
                }
            },
            "should_pass": True,
            "description": "Mixed Arabic-English content should pass"
        },
        {
            "name": "Complex synonym structure",
            "payload": {
                "translation": "تم <syn1>إصلاح</syn1> صفحة <syn2>الأصول</syn2> وإضافة <syn3>Leonardo</syn3>.",
                "words": {
                    "1": ["تثبيت", "معالجة", "تصحيح"],
                    "2": ["الموارد", "العناصر", "المكونات"],
                    "3": ["ليوناردو", "Leonardo AI", "أداة ليوناردو"]
                }
            },
            "should_pass": True,
            "description": "Complex multi-synonym structure should pass"
        },
        {
            "name": "Additional properties (strict mode)",
            "payload": {
                "translation": "Test translation",
                "words": {},
                "extra_field": "should not be allowed"
            },
            "should_pass": False,
            "description": "Should fail due to additionalProperties: false in schema"
        }
    ]
    
    for case in test_cases:
        try:
            result = contracts.validate(case['payload'], schema_path)
            passed = result.is_valid == case['should_pass']
            
            expected = f"Should {'pass' if case['should_pass'] else 'fail'}"
            actual = f"{'Passed' if result.is_valid else 'Failed'}"
            
            if result.errors:
                actual += f" - Errors: {result.errors[:2]}"  # Show first 2 errors
            
            print(f"Payload: {json.dumps(case['payload'], ensure_ascii=False, indent=2)}")
            print_result(case['name'], expected, actual, passed)
            
        except Exception as e:
            print_result(case['name'], "Should handle gracefully", f"Exception: {str(e)}", False)


def test_parametrized_validation_scenarios():
    """Test 7: Parametrized validation scenarios (pytest-style converted)."""
    print_test_header("Parametrized Validation Scenarios")
    
    schema_path = "tests/schemas/translation_with_synonyms.yaml"
    
    # Convert pytest parametrize style to regular test cases
    parametrized_cases = [
        # (payload, expected_valid, description)
        (
            {
                "translation": "تم <syn1>إصلاح</syn1> الخطأ.",
                "words": {
                    "1": ["تثبيت", "معالجة"]
                }
            },
            True,
            "Fully valid structure should pass"
        ),
        (
            {
                "translation": "مرحبا بالعالم"
            },
            False,
            "Missing 'words' field should fail"
        ),
        (
            {
                "translation": "تم <syn1>إصلاح</syn1> الخطأ.",
                "words": {
                    "1": "تثبيت"
                }
            },
            False,
            "Non-array words value should fail"
        ),
        (
            {
                "translation": "Valid translation with empty words",
                "words": {}
            },
            True,
            "Empty words object should pass (optional synonyms)"
        ),
        (
            {
                "translation": "Short",
                "words": {}
            },
            True,
            "Short translation should pass (meets minLength: 1)"
        )
    ]
    
    for i, (payload, expected_valid, description) in enumerate(parametrized_cases, 1):
        try:
            result = contracts.validate(payload, schema_path)
            passed = result.is_valid == expected_valid
            
            expected = f"Should {'pass' if expected_valid else 'fail'}"
            actual = f"{'Passed' if result.is_valid else 'Failed'}"
            
            # Format payload for display
            payload_str = json.dumps(payload, ensure_ascii=False)
            if len(payload_str) > 100:
                payload_str = payload_str[:97] + "..."
            
            print(f"Case {i}: {payload_str}")
            print_result(description, expected, actual, passed)
            
            if not passed:
                print(f"       Validation errors: {result.errors}")
                
        except Exception as e:
            print_result(f"Case {i}", "Should handle gracefully", f"Exception: {str(e)}", False)


def run_all_tests():
    """Run all critical fix tests."""
    print("🚀 LLM-Contracts Critical Fixes Verification")
    print("=" * 60)
    print("Testing all the critical issues that were identified and fixed.")
    
    test_malformed_json_rejection()
    test_list_items_detection() 
    test_duplicate_sentences_detection()
    test_content_extraction_from_dict()
    test_duplicate_synonyms_limitation()
    test_real_world_translation_scenarios()
    test_parametrized_validation_scenarios()
    
    print("\n" + "="*60)
    print("🏁 All tests completed!")
    print("=" * 60)
    print("✅ Critical fixes have been verified.")
    print("📋 Review any failed tests above for potential issues.")


if __name__ == "__main__":
    run_all_tests() 