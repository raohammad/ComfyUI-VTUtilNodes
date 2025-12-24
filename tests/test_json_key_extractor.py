import unittest
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the node
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nodes import JSONKeyExtractor


class TestJSONKeyExtractor(unittest.TestCase):
    """Test cases for the JSONKeyExtractor node"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.node = JSONKeyExtractor()
        self.test_json = {
            "song_description": {
                "music_type_prompt": "Warm, gentle",
                "song_verses_prompt": "Light piano melody"
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "time_range": "0-5s",
                    "image_edit_prompt": "A claymation character"
                },
                {
                    "scene_number": 2,
                    "time_range": "5-10s",
                    "image_edit_prompt": "Another scene"
                }
            ]
        }
    
    def test_extract_simple_key(self):
        """Test extracting a simple top-level key"""
        result = self.node.extract_value(self.test_json, "scenes")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], list)
        self.assertEqual(len(result[0]), 2)
    
    def test_extract_nested_key(self):
        """Test extracting a nested key using dot notation"""
        result = self.node.extract_value(self.test_json, "song_description.music_type_prompt")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Warm, gentle")
    
    def test_extract_array_element(self):
        """Test extracting an array element using bracket notation"""
        result = self.node.extract_value(self.test_json, "scenes[0]")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["scene_number"], 1)
        self.assertEqual(result[0]["time_range"], "0-5s")
    
    def test_extract_nested_from_array(self):
        """Test extracting a nested key from an array element"""
        result = self.node.extract_value(self.test_json, "scenes[0].scene_number")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 1)
    
    def test_extract_array_index_out_of_range(self):
        """Test handling of array index out of range"""
        result = self.node.extract_value(self.test_json, "scenes[10]")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
        self.assertEqual(result[0]["error"], "Key path not found")
    
    def test_extract_nonexistent_key(self):
        """Test handling of non-existent key"""
        result = self.node.extract_value(self.test_json, "nonexistent")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
        self.assertEqual(result[0]["error"], "Key path not found")
    
    def test_extract_nonexistent_nested_key(self):
        """Test handling of non-existent nested key"""
        result = self.node.extract_value(self.test_json, "song_description.nonexistent")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
    
    def test_extract_empty_path(self):
        """Test that empty path returns the entire input"""
        result = self.node.extract_value(self.test_json, "")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.test_json)
    
    def test_extract_from_list_input(self):
        """Test extracting from a list input"""
        list_input = [1, 2, 3, 4, 5]
        result = self.node.extract_value(list_input, "[2]")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 3)
    
    def test_extract_second_array_element(self):
        """Test extracting the second element from an array"""
        result = self.node.extract_value(self.test_json, "scenes[1]")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["scene_number"], 2)
    
    def test_extract_deeply_nested(self):
        """Test extracting from deeply nested structure"""
        deep_json = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep_value"
                    }
                }
            }
        }
        result = self.node.extract_value(deep_json, "level1.level2.level3.value")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "deep_value")
    
    def test_extract_primitive_value(self):
        """Test extracting a primitive value (string input)"""
        result = self.node.extract_value("hello", "")
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "hello")
    
    def test_input_types(self):
        """Test that INPUT_TYPES is correctly defined"""
        input_types = JSONKeyExtractor.INPUT_TYPES()
        
        self.assertIn("required", input_types)
        self.assertIn("json_input", input_types["required"])
        self.assertIn("key_path", input_types["required"])
        self.assertEqual(input_types["required"]["json_input"][0], "*")
        self.assertEqual(input_types["required"]["key_path"][0], "STRING")
    
    def test_return_types(self):
        """Test that RETURN_TYPES is correctly defined"""
        self.assertEqual(JSONKeyExtractor.RETURN_TYPES, ("*",))
        self.assertEqual(JSONKeyExtractor.RETURN_NAMES, ("value",))
        self.assertEqual(JSONKeyExtractor.FUNCTION, "extract_value")
        self.assertEqual(JSONKeyExtractor.CATEGORY, "VTUtil")
    
    def test_extract_with_whitespace(self):
        """Test that key path with whitespace is handled"""
        result = self.node.extract_value(self.test_json, "  scenes  ")
        
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], list)
        self.assertEqual(len(result[0]), 2)


if __name__ == '__main__':
    unittest.main()

