import unittest
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the node
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nodes import JSONQueue


class TestJSONQueue(unittest.TestCase):
    """Test cases for the JSONQueue node"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.node = JSONQueue()
        # Reset queues before each test
        JSONQueue._queues.clear()
        JSONQueue._current_outputs.clear()
        JSONQueue._last_signal.clear()
        JSONQueue._initialized.clear()
        JSONQueue._item_index.clear()
    
    def test_first_item_outputs_immediately(self):
        """Test that first item is output immediately without signal"""
        result = self.node.process_queue({"scene": 1}, "test_queue", False, 0)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]["scene"], 1)
        self.assertEqual(result[1], 0)  # Queue length
        self.assertEqual(result[2], False)  # Has more
        self.assertEqual(result[3], 0)  # Item index
    
    def test_second_item_waits_for_signal(self):
        """Test that second item waits in queue until signal increments"""
        # Add first item (outputs immediately)
        result1 = self.node.process_queue({"scene": 1}, "test_queue", False, 0)
        self.assertEqual(result1[0]["scene"], 1)
        
        # Add second item (should stay in queue)
        result2 = self.node.process_queue({"scene": 2}, "test_queue", False, 0)
        self.assertEqual(result2[0]["scene"], 1)  # Still first item
        self.assertEqual(result2[1], 1)  # Queue length is 1
        self.assertEqual(result2[2], True)  # Has more
        self.assertEqual(result2[3], 0)  # Still index 0
    
    def test_signal_increment_outputs_next_item(self):
        """Test that signal increment outputs next item"""
        # Add first item
        self.node.process_queue({"scene": 1}, "test_queue", False, 0)
        
        # Add second item
        self.node.process_queue({"scene": 2}, "test_queue", False, 0)
        
        # Increment signal (should output second item)
        result = self.node.process_queue(None, "test_queue", False, 1)
        self.assertEqual(result[0]["scene"], 2)
        self.assertEqual(result[1], 0)  # Queue is empty
        self.assertEqual(result[2], False)  # No more items
        self.assertEqual(result[3], 1)  # Index is 1
    
    def test_multiple_items_in_queue(self):
        """Test processing multiple items in queue"""
        # Add first item (outputs immediately)
        result1 = self.node.process_queue({"scene": 1}, "test_queue", False, 0)
        self.assertEqual(result1[0]["scene"], 1)
        self.assertEqual(result1[3], 0)
        
        # Add second and third items
        self.node.process_queue({"scene": 2}, "test_queue", False, 0)
        self.node.process_queue({"scene": 3}, "test_queue", False, 0)
        
        # Signal increment 1 (outputs scene 2)
        result2 = self.node.process_queue(None, "test_queue", False, 1)
        self.assertEqual(result2[0]["scene"], 2)
        self.assertEqual(result2[1], 1)  # One item left
        self.assertEqual(result2[2], True)  # Has more
        self.assertEqual(result2[3], 1)
        
        # Signal increment 2 (outputs scene 3)
        result3 = self.node.process_queue(None, "test_queue", False, 2)
        self.assertEqual(result3[0]["scene"], 3)
        self.assertEqual(result3[1], 0)  # Queue empty
        self.assertEqual(result3[2], False)  # No more
        self.assertEqual(result3[3], 2)
    
    def test_list_input_adds_all_items(self):
        """Test that list input adds all items to queue"""
        scenes = [{"scene": 1}, {"scene": 2}, {"scene": 3}]
        
        # Add list (first item outputs immediately)
        result = self.node.process_queue(scenes, "test_queue", False, 0)
        self.assertEqual(result[0]["scene"], 1)
        self.assertEqual(result[1], 2)  # Two items in queue
        self.assertEqual(result[2], True)  # Has more
        self.assertEqual(result[3], 0)
        
        # Signal increment (outputs scene 2)
        result2 = self.node.process_queue(None, "test_queue", False, 1)
        self.assertEqual(result2[0]["scene"], 2)
        self.assertEqual(result2[1], 1)  # One item left
        self.assertEqual(result2[3], 1)
    
    def test_reset_clears_queue(self):
        """Test that reset clears the queue"""
        # Add items
        self.node.process_queue({"scene": 1}, "test_queue", False, 0)
        self.node.process_queue({"scene": 2}, "test_queue", False, 0)
        
        # Reset
        result = self.node.process_queue(None, "test_queue", True, 0)
        self.assertIsNone(result[0])
        self.assertEqual(result[1], 0)
        self.assertEqual(result[2], False)
        self.assertEqual(result[3], -1)
    
    def test_different_queue_ids(self):
        """Test that different queue IDs maintain separate queues"""
        # Add to queue 1
        result1 = self.node.process_queue({"scene": 1}, "queue1", False, 0)
        self.assertEqual(result1[0]["scene"], 1)
        
        # Add to queue 2
        result2 = self.node.process_queue({"scene": 10}, "queue2", False, 0)
        self.assertEqual(result2[0]["scene"], 10)
        
        # Verify they're separate
        self.assertNotEqual(result1[0], result2[0])
    
    def test_signal_same_value_no_change(self):
        """Test that same signal value doesn't advance queue"""
        # Add first item
        self.node.process_queue({"scene": 1}, "test_queue", False, 0)
        
        # Add second item
        self.node.process_queue({"scene": 2}, "test_queue", False, 0)
        
        # Same signal (should not advance)
        result1 = self.node.process_queue(None, "test_queue", False, 0)
        self.assertEqual(result1[0]["scene"], 1)  # Still first item
        self.assertEqual(result1[1], 1)  # Queue length still 1
        
        # Same signal again (should not advance)
        result2 = self.node.process_queue(None, "test_queue", False, 0)
        self.assertEqual(result2[0]["scene"], 1)  # Still first item
    
    def test_empty_queue_returns_none(self):
        """Test that empty queue returns None"""
        result = self.node.process_queue(None, "test_queue", True, 0)
        self.assertIsNone(result[0])
        self.assertEqual(result[1], 0)
        self.assertEqual(result[2], False)
        self.assertEqual(result[3], -1)
    
    def test_input_types(self):
        """Test that INPUT_TYPES is correctly defined"""
        input_types = JSONQueue.INPUT_TYPES()
        
        self.assertIn("required", input_types)
        self.assertIn("json_item", input_types["required"])
        self.assertIn("queue_id", input_types["required"])
        self.assertIn("reset", input_types["required"])
        self.assertIn("optional", input_types)
        self.assertIn("signal", input_types["optional"])
        self.assertEqual(input_types["required"]["json_item"][0], "*")
        self.assertEqual(input_types["required"]["queue_id"][0], "STRING")
        self.assertEqual(input_types["required"]["reset"][0], "BOOLEAN")
        self.assertEqual(input_types["optional"]["signal"][0], "INT")
    
    def test_return_types(self):
        """Test that RETURN_TYPES is correctly defined"""
        self.assertEqual(JSONQueue.RETURN_TYPES, ("*", "INT", "BOOLEAN", "INT"))
        self.assertEqual(JSONQueue.RETURN_NAMES, ("item", "queue_length", "has_more", "item_index"))
        self.assertEqual(JSONQueue.FUNCTION, "process_queue")
        self.assertEqual(JSONQueue.CATEGORY, "VTUtil")


if __name__ == '__main__':
    unittest.main()

