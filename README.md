# ComfyUI-VTUtilNodes

A collection of utility custom nodes for ComfyUI.

## Installation

1. Navigate to your ComfyUI `custom_nodes` directory
2. Clone this repository:
   ```bash
   git clone <repository-url> ComfyUI-VTUtilNodes
   ```
3. Restart ComfyUI

## Nodes

### TextToJSON

Converts text input to JSON object output.

- **Input**: Text string (can be valid or invalid JSON)
- **Output**: JSON object (dict, list, or primitive) - can connect to JSON inputs
- **Category**: VTUtil

If the input text is valid JSON, it will be parsed and returned as a Python object. If the input is invalid JSON, the output will be a JSON object containing error information. The node also auto-fixes common issues like missing outer braces.

**Example:**
- Input: `{"name":"hamoud"}` or `"name":"hamoud"`
- Output: `{'name': 'hamoud'}` (Python dict object)

### JSONKeyExtractor

Extracts a value from a JSON object using a key path.

- **Input**: JSON object (from TextToJSON or any JSON source)
- **Key Path**: String specifying the path to extract
- **Output**: Extracted value (can be any type)
- **Category**: VTUtil

Supports:
- Simple keys: `"scenes"`
- Nested keys: `"song_description.music_type_prompt"`
- Array indices: `"scenes[0]"`
- Combined: `"scenes[0].scene_number"`

**Examples:**
- Extract array: Key path `"scenes"` → Returns the scenes array
- Extract nested value: Key path `"song_description.music_type_prompt"` → Returns the prompt string
- Extract array element: Key path `"scenes[0]"` → Returns the first scene object
- Extract from array: Key path `"scenes[0].scene_number"` → Returns `1`

If the key path doesn't exist, returns an error object with helpful information about available keys.

## Development

### Running Tests

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests
```

## License

Apache 2.0

