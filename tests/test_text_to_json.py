import unittest
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the node
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nodes import TextToJSON


class TestTextToJSON(unittest.TestCase):
    """Test cases for the TextToJSON node"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.node = TextToJSON()
    
    def test_valid_json_object(self):
        """Test conversion of valid JSON object string"""
        input_text = '{"name": "test", "value": 123}'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Parse the result to verify it's valid JSON
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result["name"], "test")
        self.assertEqual(parsed_result["value"], 123)
    
    def test_valid_json_array(self):
        """Test conversion of valid JSON array string"""
        input_text = '[1, 2, 3, "test"]'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Parse the result to verify it's valid JSON
        parsed_result = json.loads(result[0])
        self.assertIsInstance(parsed_result, list)
        self.assertEqual(parsed_result, [1, 2, 3, "test"])
    
    def test_valid_json_string(self):
        """Test conversion of valid JSON string value"""
        input_text = '"hello world"'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Parse the result to verify it's valid JSON
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result, "hello world")
    
    def test_valid_json_number(self):
        """Test conversion of valid JSON number"""
        input_text = '42'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Parse the result to verify it's valid JSON
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result, 42)
    
    def test_invalid_json(self):
        """Test handling of invalid JSON input"""
        input_text = '{"name": "test", invalid}'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Parse the result - it should be a JSON object with error information
        parsed_result = json.loads(result[0])
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Invalid JSON input")
        self.assertIn("original_text", parsed_result)
    
    def test_empty_string(self):
        """Test handling of empty string - now returns empty object"""
        input_text = ''
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Empty string now returns empty JSON object
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result, {})
    
    def test_formatted_output(self):
        """Test that output is properly formatted with indentation"""
        input_text = '{"a":1,"b":2,"c":3}'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        # Check that the output contains newlines (indentation)
        self.assertIn('\n', result[0])
        
        # Verify it's still valid JSON
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result["a"], 1)
        self.assertEqual(parsed_result["b"], 2)
        self.assertEqual(parsed_result["c"], 3)
    
    def test_nested_json(self):
        """Test conversion of nested JSON structures"""
        input_text = '{"level1": {"level2": {"level3": "deep"}}}'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result["level1"]["level2"]["level3"], "deep")
    
    def test_input_types(self):
        """Test that INPUT_TYPES is correctly defined"""
        input_types = TextToJSON.INPUT_TYPES()
        
        self.assertIn("required", input_types)
        self.assertIn("text", input_types["required"])
        self.assertEqual(input_types["required"]["text"][0], "STRING")
    
    def test_return_types(self):
        """Test that RETURN_TYPES is correctly defined"""
        self.assertEqual(TextToJSON.RETURN_TYPES, ("STRING",))
        self.assertEqual(TextToJSON.RETURN_NAMES, ("json",))
        self.assertEqual(TextToJSON.FUNCTION, "convert_to_json")
        self.assertEqual(TextToJSON.CATEGORY, "VTUtil")
    
    def test_missing_outer_braces_auto_fix(self):
        """Test auto-fix for JSON missing outer braces"""
        # This is the exact case the user reported
        input_text = '"name":"nammad"'
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        
        # Should be successfully parsed (auto-fixed)
        parsed_result = json.loads(result[0])
        self.assertNotIn("error", parsed_result)
        self.assertEqual(parsed_result["name"], "nammad")
    
    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is stripped"""
        input_text = '   {"name": "test"}   '
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result["name"], "test")
    
    def test_empty_string_returns_empty_object(self):
        """Test that empty string returns empty JSON object"""
        input_text = ''
        result = self.node.convert_to_json(input_text)
        
        self.assertIsInstance(result, tuple)
        parsed_result = json.loads(result[0])
        self.assertEqual(parsed_result, {})


if __name__ == '__main__':
    unittest.main()

