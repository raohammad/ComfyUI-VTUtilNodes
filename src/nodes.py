import json
from typing import Tuple


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
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json",)
    FUNCTION = "convert_to_json"
    OUTPUT_NODE = False
    
    def convert_to_json(self, text: str) -> Tuple[str]:
        """
        Convert text input to JSON format.
        
        Args:
            text: Input text string that should be valid JSON
            
        Returns:
            Tuple containing the JSON string representation
        """
        try:
            # Try to parse the text as JSON to validate it
            parsed = json.loads(text)
            # Return the formatted JSON string
            result = json.dumps(parsed, indent=2, ensure_ascii=False)
            return (result,)
        except json.JSONDecodeError as e:
            # If text is not valid JSON, wrap it in a JSON object with an error message
            # or return it as a JSON string value
            error_result = json.dumps({
                "error": "Invalid JSON input",
                "message": str(e),
                "original_text": text
            }, indent=2, ensure_ascii=False)
            return (error_result,)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "TextToJSON": TextToJSON,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToJSON": "Text to JSON",
}

