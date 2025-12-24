import unittest
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the node
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nodes import JSONListIterator


class TestJSONListIterator(unittest.TestCase):
    """Test cases for the JSONListIterator node"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.node = JSONListIterator()
        self.test_list = [
            {
                "scene_number": 1,
                "time_range": "0-5s",
                "image_edit_prompt": "Scene 1 prompt",
                "has_dialogue": False
            },
            {
                "scene_number": 2,
                "time_range": "5-10s",
                "image_edit_prompt": "Scene 2 prompt",
                "has_dialogue": True,
                "dialogues": [{"text": "Hello"}]
            },
            {
                "scene_number": 3,
                "time_range": "10-15s",
                "image_edit_prompt": "Scene 3 prompt",
                "has_dialogue": False
            }
        ]
    
    def test_extract_first_item(self):
        """Test extracting the first item from a list"""
        result = self.node.get_item(self.test_list, 0)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["scene_number"], 1)
        self.assertEqual(result[0]["time_range"], "0-5s")
        self.assertEqual(result[1], 0)  # Index returned
    
    def test_extract_second_item(self):
        """Test extracting the second item from a list"""
        result = self.node.get_item(self.test_list, 1)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["scene_number"], 2)
        self.assertEqual(result[1], 1)  # Index returned
    
    def test_extract_last_item(self):
        """Test extracting the last item from a list"""
        result = self.node.get_item(self.test_list, 2)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["scene_number"], 3)
        self.assertEqual(result[1], 2)  # Index returned
    
    def test_index_out_of_range(self):
        """Test handling of index out of range"""
        result = self.node.get_item(self.test_list, 10)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
        self.assertEqual(result[0]["error"], "Index out of range")
        self.assertEqual(result[0]["list_length"], 3)
        self.assertEqual(result[0]["requested_index"], 10)
        self.assertEqual(result[1], 10)  # Index still returned
    
    def test_negative_index(self):
        """Test negative index (Python-style)"""
        result = self.node.get_item(self.test_list, -1)
        
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["scene_number"], 3)  # Last item
    
    def test_dict_input(self):
        """Test handling of dict input (not a list)"""
        test_dict = {"key": "value"}
        result = self.node.get_item(test_dict, 0)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], test_dict)  # Returns the dict itself
        self.assertEqual(result[1], 0)
    
    def test_dict_input_invalid_index(self):
        """Test dict input with invalid index"""
        test_dict = {"key": "value"}
        result = self.node.get_item(test_dict, 1)
        
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
        self.assertEqual(result[0]["error"], "Not a list")
    
    def test_primitive_input(self):
        """Test handling of primitive input"""
        result = self.node.get_item("hello", 0)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], "hello")
        self.assertEqual(result[1], 0)
    
    def test_primitive_input_invalid_index(self):
        """Test primitive input with invalid index"""
        result = self.node.get_item("hello", 1)
        
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
        self.assertEqual(result[0]["error"], "Not a list")
    
    def test_empty_list(self):
        """Test handling of empty list"""
        empty_list = []
        result = self.node.get_item(empty_list, 0)
        
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], dict)
        self.assertIn("error", result[0])
        self.assertEqual(result[0]["error"], "Index out of range")
        self.assertEqual(result[0]["list_length"], 0)
    
    def test_input_types(self):
        """Test that INPUT_TYPES is correctly defined"""
        input_types = JSONListIterator.INPUT_TYPES()
        
        self.assertIn("required", input_types)
        self.assertIn("json_list", input_types["required"])
        self.assertIn("index", input_types["required"])
        self.assertEqual(input_types["required"]["json_list"][0], "*")
        self.assertEqual(input_types["required"]["index"][0], "INT")
    
    def test_return_types(self):
        """Test that RETURN_TYPES is correctly defined"""
        self.assertEqual(JSONListIterator.RETURN_TYPES, ("*", "INT"))
        self.assertEqual(JSONListIterator.RETURN_NAMES, ("item", "index"))
        self.assertEqual(JSONListIterator.FUNCTION, "get_item")
        self.assertEqual(JSONListIterator.CATEGORY, "VTUtil")
    
    def test_all_items_in_sequence(self):
        """Test extracting all items in sequence"""
        for i in range(len(self.test_list)):
            result = self.node.get_item(self.test_list, i)
            self.assertIsInstance(result[0], dict)
            self.assertEqual(result[0]["scene_number"], i + 1)
            self.assertEqual(result[1], i)


if __name__ == '__main__':
    unittest.main()

