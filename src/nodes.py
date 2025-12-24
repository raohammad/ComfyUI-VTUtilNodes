import json
from typing import Tuple, Union, Any


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
    """
    CATEGORY = "VTUtil"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_list": ("*", {
                    "forceInput": True,
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "step": 1,
                    "tooltip": "Index of the item to extract from the list (0-based)"
                }),
            }
        }
    
    RETURN_TYPES = ("*", "INT")
    RETURN_NAMES = ("item", "index")
    FUNCTION = "get_item"
    OUTPUT_NODE = False
    
    def get_item(self, json_list: Union[list, dict, Any], index: int) -> Tuple[Union[dict, list, str, int, float, bool, None], int]:
        """
        Extract an item from a JSON list by index.
        
        Args:
            json_list: The JSON list (or dict/other) to extract from
            index: The index of the item to extract (0-based)
            
        Returns:
            Tuple containing the item at the specified index and the current index
        """
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


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "TextToJSON": TextToJSON,
    "JSONKeyExtractor": JSONKeyExtractor,
    "JSONListIterator": JSONListIterator,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToJSON": "Text to JSON",
    "JSONKeyExtractor": "JSON Key Extractor",
    "JSONListIterator": "JSON List Iterator",
}

