import json
from typing import Tuple, Union


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


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "TextToJSON": TextToJSON,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToJSON": "Text to JSON",
}

