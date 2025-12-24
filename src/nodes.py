import json
from typing import Tuple, Union, Any
from collections import deque


class TextToJSON:
    """
    A custom node that takes text input and converts it to JSON format.
    The text is parsed as JSON and returned as a JSON string output.
    """
    CATEGORY = "VTUtil"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            }
        }
    
    RETURN_TYPES = ("*",)  # Use wildcard to allow connection to any type, or use dict/list
    RETURN_NAMES = ("json",)
    FUNCTION = "convert_to_json"
    OUTPUT_NODE = False
    
    def convert_to_json(self, text: str) -> Tuple[Union[dict, list, str, int, float, bool, None]]:
        """
        Convert text input to JSON format and return the parsed object.
        
        Args:
            text: Input text string that should be valid JSON
            
        Returns:
            Tuple containing the parsed JSON object (dict, list, or primitive)
        """
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Handle empty input
        if not text:
            return ({},)
        
        try:
            # Try to parse the text as JSON to validate it
            parsed = json.loads(text)
            # Return the parsed object directly (not a string)
            return (parsed,)
        except json.JSONDecodeError as e:
            # Try to auto-fix common issues
            fixed_text = self._try_fix_json(text)
            if fixed_text != text:
                try:
                    parsed = json.loads(fixed_text)
                    return (parsed,)
                except json.JSONDecodeError:
                    pass  # Fall through to error handling
            
            # If text is not valid JSON, return an error object
            error_result = {
                "error": "Invalid JSON input",
                "message": str(e),
                "original_text": text,
                "hint": "Make sure your JSON has proper quotes and braces. Example: {\"key\": \"value\"}"
            }
            return (error_result,)
    
    def _try_fix_json(self, text: str) -> str:
        """
        Try to fix common JSON issues like missing outer braces.
        
        Args:
            text: Potentially malformed JSON string
            
        Returns:
            Fixed JSON string (or original if no fix could be applied)
        """
        text = text.strip()
        
        # If text looks like object content but missing outer braces
        # e.g., "name":"value" -> {"name":"value"}
        # Pattern: starts with a quoted string followed by colon
        if not text.startswith('{') and not text.startswith('['):
            # Check if it starts with a quoted key (like "key":)
            import re
            # Pattern matches: "key":value or "key":"value"
            if re.match(r'^"[^"]+"\s*:', text):
                # Try wrapping in braces
                fixed = '{' + text + '}'
                return fixed
        
        return text


class JSONKeyExtractor:
    """
    A custom node that extracts a value from a JSON object using a key path.
    Supports nested keys using dot notation (e.g., "level1.level2.key")
    and array indices using bracket notation (e.g., "scenes[0]" or "scenes[0].name").
    """
    CATEGORY = "VTUtil"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_input": ("*", {
                    "forceInput": True,
                }),
                "key_path": ("STRING", {
                    "multiline": False,
                    "default": "scenes",
                    "tooltip": "Key path to extract. Use dot notation for nested keys (e.g., 'level1.level2.key') or bracket notation for arrays (e.g., 'scenes[0]' or 'scenes[0].name')"
                }),
            }
        }
    
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("value",)
    FUNCTION = "extract_value"
    OUTPUT_NODE = False
    
    def extract_value(self, json_input: Union[dict, list, str, int, float, bool, None], key_path: str) -> Tuple[Union[dict, list, str, int, float, bool, None]]:
        """
        Extract a value from a JSON object using a key path.
        
        Args:
            json_input: The JSON object (dict, list, or primitive) to extract from
            key_path: The key path to extract (supports dot notation and array indices)
            
        Returns:
            Tuple containing the extracted value, or an error dict if not found
        """
        if not key_path or not key_path.strip():
            return (json_input,)
        
        key_path = key_path.strip()
        
        try:
            result = self._extract_by_path(json_input, key_path)
            return (result,)
        except (KeyError, IndexError, TypeError) as e:
            # Return an error object if the key path doesn't exist
            error_result = {
                "error": "Key path not found",
                "message": str(e),
                "key_path": key_path,
                "available_keys": self._get_available_keys(json_input) if isinstance(json_input, (dict, list)) else None
            }
            return (error_result,)
    
    def _extract_by_path(self, data: Union[dict, list, Any], path: str) -> Any:
        """
        Extract a value from data using a key path.
        Supports:
        - Simple keys: "name"
        - Nested keys: "level1.level2.key"
        - Array indices: "scenes[0]"
        - Combined: "scenes[0].name"
        
        Args:
            data: The data structure to extract from
            path: The key path
            
        Returns:
            The extracted value
            
        Raises:
            KeyError: If a key doesn't exist
            IndexError: If an array index is out of bounds
            TypeError: If trying to access a key on a non-dict/list
        """
        # Split the path into parts, handling both dot notation and bracket notation
        # Pattern: matches keys like "name", "level1", "scenes[0]", etc.
        parts = []
        current = ""
        i = 0
        
        while i < len(path):
            char = path[i]
            
            if char == '.':
                if current:
                    parts.append(current)
                    current = ""
            elif char == '[':
                # Found array index
                if current:
                    parts.append(current)
                    current = ""
                # Find the closing bracket
                i += 1
                index_str = ""
                while i < len(path) and path[i] != ']':
                    index_str += path[i]
                    i += 1
                if i < len(path) and path[i] == ']':
                    try:
                        index = int(index_str)
                        parts.append(index)
                    except ValueError:
                        raise ValueError(f"Invalid array index: {index_str}")
                else:
                    raise ValueError(f"Unclosed bracket in path: {path}")
            else:
                current += char
            i += 1
        
        if current:
            parts.append(current)
        
        # Navigate through the data structure
        current_data = data
        
        for part in parts:
            if isinstance(current_data, dict):
                if isinstance(part, int):
                    raise TypeError(f"Cannot use integer index on dict. Path: {path}")
                if part not in current_data:
                    raise KeyError(f"Key '{part}' not found in object. Path: {path}")
                current_data = current_data[part]
            elif isinstance(current_data, list):
                if isinstance(part, int):
                    if part < 0 or part >= len(current_data):
                        raise IndexError(f"Index {part} out of range for list of length {len(current_data)}. Path: {path}")
                    current_data = current_data[part]
                else:
                    # Try to find the key in list items (if they're dicts)
                    found = False
                    for item in current_data:
                        if isinstance(item, dict) and part in item:
                            current_data = item[part]
                            found = True
                            break
                    if not found:
                        raise KeyError(f"Key '{part}' not found in list items. Path: {path}")
            else:
                raise TypeError(f"Cannot access key '{part}' on type {type(current_data).__name__}. Path: {path}")
        
        return current_data
    
    def _get_available_keys(self, data: Union[dict, list], max_depth: int = 2, current_depth: int = 0) -> Union[list, dict]:
        """
        Get available keys from a data structure for error messages.
        
        Args:
            data: The data structure
            max_depth: Maximum depth to traverse
            current_depth: Current depth
            
        Returns:
            List or dict of available keys
        """
        if current_depth >= max_depth:
            return "..."
        
        if isinstance(data, dict):
            result = {}
            for key, value in list(data.items())[:5]:  # Limit to first 5 keys
                if isinstance(value, (dict, list)):
                    result[key] = self._get_available_keys(value, max_depth, current_depth + 1)
                else:
                    result[key] = type(value).__name__
            if len(data) > 5:
                result["..."] = f"and {len(data) - 5} more keys"
            return result
        elif isinstance(data, list):
            if len(data) > 0:
                return f"Array with {len(data)} items. First item keys: {self._get_available_keys(data[0], max_depth, current_depth + 1) if isinstance(data[0], (dict, list)) else type(data[0]).__name__}"
            return "Empty array"
        else:
            return type(data).__name__

class JSONListIterator:
    """
    A custom node that takes a JSON list and outputs individual items one by one.
    Can be used to iterate through arrays like scenes, processing each item individually.
    Supports both indexed extraction and outputting all items.
    """
    CATEGORY = "VTUtil"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_list": ("*", {
                    "forceInput": True,
                }),
                "mode": (["single", "all"], {
                    "default": "single",
                    "tooltip": "single: Extract one item by index | all: Output all items as a list"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "step": 1,
                    "tooltip": "Index of the item to extract from the list (0-based). Only used when mode is 'single'"
                }),
            }
        }
    
    RETURN_TYPES = ("*", "INT")
    RETURN_NAMES = ("item", "index")
    FUNCTION = "get_item"
    OUTPUT_NODE = False
    
    def get_item(self, json_list: Union[list, dict, Any], mode: str, index: int) -> Tuple[Union[dict, list, str, int, float, bool, None], int]:
        """
        Extract item(s) from a JSON list.
        
        Args:
            json_list: The JSON list (or dict/other) to extract from
            mode: "single" to extract one item by index, "all" to output all items
            index: The index of the item to extract (0-based, only used when mode is "single")
            
        Returns:
            Tuple containing:
            - If mode is "single": The item at the specified index
            - If mode is "all": A list containing all items (or the original input if not a list)
            - The current index (or -1 if mode is "all")
        """
        # If mode is "all", return all items
        if mode == "all":
            if isinstance(json_list, list):
                # Return all items as a list
                return (json_list, -1)
            elif isinstance(json_list, dict):
                # For dict, return it wrapped in a list
                return ([json_list], -1)
            else:
                # For primitives, wrap in a list
                return ([json_list], -1)
        
        # Mode is "single" - extract by index
        # If input is a list, extract by index
        if isinstance(json_list, list):
            if index < 0:
                index = len(json_list) + index  # Support negative indices
            if index < 0 or index >= len(json_list):
                # Return error object if index is out of range
                error_result = {
                    "error": "Index out of range",
                    "message": f"Index {index} is out of range for list of length {len(json_list)}",
                    "list_length": len(json_list),
                    "requested_index": index
                }
                return (error_result, index)
            return (json_list[index], index)
        
        # If input is a dict, try to treat it as a single-item list
        elif isinstance(json_list, dict):
            if index == 0:
                return (json_list, index)
            else:
                error_result = {
                    "error": "Not a list",
                    "message": "Input is a dict, not a list. Only index 0 is valid.",
                    "input_type": "dict"
                }
                return (error_result, index)
        
        # If input is a primitive, return it if index is 0
        else:
            if index == 0:
                return (json_list, index)
            else:
                error_result = {
                    "error": "Not a list",
                    "message": "Input is not a list or dict. Only index 0 is valid.",
                    "input_type": type(json_list).__name__
                }
                return (error_result, index)


class JSONQueue:
    """
    A FIFO queue node that receives JSON items one by one and outputs them sequentially.
    The first item is output immediately, subsequent items require a signal to proceed.
    This allows processing each item through the same workflow pipeline.
    
    Usage:
    1. Connect JSONListIterator output to json_item input
    2. First item is output immediately without signal
    3. Connect a signal (e.g., from end of processing pipeline) to signal input
    4. When signal increments, next item is output
    5. Use same queue_id for all items in the same queue
    """
    CATEGORY = "VTUtil"
    
    # Class-level queue storage (shared across all instances)
    _queues = {}
    _current_outputs = {}
    _last_signal = {}
    _initialized = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_item": ("*", {
                    "forceInput": True,
                }),
                "queue_id": ("STRING", {
                    "default": "default",
                    "tooltip": "Unique identifier for this queue. Use the same ID for all items in the same queue."
                }),
                "reset": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reset the queue (clears all items and starts fresh). Set to True to start a new queue."
                }),
            },
            "optional": {
                "signal": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "tooltip": "Signal to advance to next item. Connect this to a counter or completion signal from your processing pipeline. Increment this value to process next item in queue. IMPORTANT: Do NOT connect this directly to the same JSONQueue's item output - connect it from the END of your processing pipeline."
                }),
            }
        }
    
    RETURN_TYPES = ("*", "INT", "BOOLEAN", "INT")
    RETURN_NAMES = ("item", "queue_length", "has_more", "item_index")
    FUNCTION = "process_queue"
    OUTPUT_NODE = False
    
    def process_queue(self, json_item: Union[dict, list, Any], queue_id: str, reset: bool, signal: Union[int, None] = None) -> Tuple[Union[dict, list, Any], int, bool, int]:
        """
        Process items in a FIFO queue.
        
        Args:
            json_item: The JSON item to add to the queue or process
            queue_id: Unique identifier for this queue
            reset: If True, clear the queue and start fresh
            signal: Signal value to advance to next item (increment to process next). Can be None.
            
        Returns:
            Tuple containing:
            - The current item to process (or None if queue is empty)
            - The remaining queue length
            - Boolean indicating if there are more items
            - The index of the current item (0-based)
        """
        # Handle None signal (when not connected)
        if signal is None:
            signal = 0
        
        # Initialize queue if it doesn't exist or if reset is requested
        if reset or queue_id not in self._queues:
            self._queues[queue_id] = deque()
            self._current_outputs[queue_id] = None
            self._last_signal[queue_id] = -1
            self._initialized[queue_id] = False
            self._item_index[queue_id] = -1
        
        # Initialize item_index tracking if needed
        if not hasattr(self, '_item_index'):
            self._item_index = {}
        if queue_id not in self._item_index:
            self._item_index[queue_id] = -1
        
        queue = self._queues[queue_id]
        
        # If reset, clear everything
        if reset:
            queue.clear()
            self._current_outputs[queue_id] = None
            self._last_signal[queue_id] = -1
            self._initialized[queue_id] = False
            self._item_index[queue_id] = -1
        
        # Add the new item to the queue (if it's not None/empty)
        if json_item is not None:
            # Check if this is a list - if so, add all items to queue
            if isinstance(json_item, list):
                queue.extend(json_item)
            else:
                queue.append(json_item)
        
        # Check if signal has changed (incremented)
        signal_changed = signal > self._last_signal[queue_id]
        
        # If queue is empty and nothing is being processed, return None
        if len(queue) == 0 and not self._initialized[queue_id]:
            return (None, 0, False, -1)
        
        # First item: output immediately (if not initialized yet)
        if not self._initialized[queue_id] and len(queue) > 0:
            item = queue.popleft()
            self._current_outputs[queue_id] = item
            self._last_signal[queue_id] = signal
            self._initialized[queue_id] = True
            self._item_index[queue_id] = 0
            return (item, len(queue), len(queue) > 0, 0)
        
        # Subsequent items: only output if signal has changed (incremented)
        if signal_changed:
            if len(queue) > 0:
                item = queue.popleft()
                self._current_outputs[queue_id] = item
                self._last_signal[queue_id] = signal
                self._item_index[queue_id] += 1
                return (item, len(queue), len(queue) > 0, self._item_index[queue_id])
            else:
                # Queue is empty, return current output
                return (self._current_outputs[queue_id], 0, False, self._item_index[queue_id])
        
        # Signal hasn't changed, return current output
        return (self._current_outputs[queue_id], len(queue), len(queue) > 0, self._item_index[queue_id])


# Initialize class-level tracking
JSONQueue._item_index = {}


class SignalCounter:
    """
    A simple counter node that generates incrementing signals.
    Can be used to trigger the next item in a JSONQueue.
    Each execution increments the counter, making it perfect for completion signals.
    """
    CATEGORY = "VTUtil"
    
    # Class-level counter storage
    _counters = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger": ("VIDEO", {
                    "forceInput": True,
                    "tooltip": "Video output that triggers the counter. Connect your video generation node output here. The value itself is not used, only the execution triggers the counter."
                }),
                "counter_id": ("STRING", {
                    "default": "default",
                    "tooltip": "Unique identifier for this counter. Use the same ID to maintain counter state."
                }),
                "reset": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reset the counter to 0"
                }),
            }
        }
    
    RETURN_TYPES = ("INT", "INT", "BOOLEAN")
    RETURN_NAMES = ("signal", "count", "is_first")
    FUNCTION = "increment_counter"
    OUTPUT_NODE = False
    
    def increment_counter(self, trigger: Any, counter_id: str, reset: bool) -> Tuple[int, int, bool]:
        """
        Increment a counter each time this node executes.
        
        Args:
            trigger: Any input that triggers the counter (video output, completion signal, etc.)
            counter_id: Unique identifier for this counter
            reset: If True, reset counter to 0
            
        Returns:
            Tuple containing:
            - Signal value (current count, use this for JSONQueue signal input)
            - Count value (same as signal, for display)
            - Is first (True if this is the first execution, False otherwise)
        """
        # Initialize counter if needed
        if counter_id not in self._counters or reset:
            self._counters[counter_id] = 0
        
        # Get current count
        current_count = self._counters[counter_id]
        is_first = (current_count == 0)
        
        # Increment counter (unless reset, then start at 0)
        if not reset:
            self._counters[counter_id] += 1
            return (self._counters[counter_id], self._counters[counter_id], is_first)
        else:
            self._counters[counter_id] = 0
            return (0, 0, True)


class SimpleCounter:
    """
    A simpler counter that just increments on each execution.
    No trigger needed - just connect the output to JSONQueue signal input.
    """
    CATEGORY = "VTUtil"
    
    _counters = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "counter_id": ("STRING", {
                    "default": "default",
                    "tooltip": "Unique identifier for this counter"
                }),
                "reset": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reset the counter to 0"
                }),
            }
        }
    
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("signal",)
    FUNCTION = "increment"
    OUTPUT_NODE = False
    
    def increment(self, counter_id: str, reset: bool) -> Tuple[int]:
        """
        Simple counter that increments on each execution.
        
        Args:
            counter_id: Unique identifier for this counter
            reset: If True, reset counter to 0
            
        Returns:
            Tuple containing the current signal value
        """
        if counter_id not in self._counters or reset:
            self._counters[counter_id] = 0
        
        if not reset:
            self._counters[counter_id] += 1
        
        return (self._counters[counter_id],)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "TextToJSON": TextToJSON,
    "JSONKeyExtractor": JSONKeyExtractor,
    "JSONListIterator": JSONListIterator,
    "JSONQueue": JSONQueue,
    "SignalCounter": SignalCounter,
    "SimpleCounter": SimpleCounter,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToJSON": "Text to JSON",
    "JSONKeyExtractor": "JSON Key Extractor",
    "JSONListIterator": "JSON List Iterator",
    "JSONQueue": "JSON Queue",
    "SignalCounter": "Signal Counter",
    "SimpleCounter": "Simple Counter",
}

