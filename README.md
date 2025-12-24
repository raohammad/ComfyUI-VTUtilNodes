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

### JSONListIterator

Extracts individual items from a JSON list by index, or outputs all items at once. Allows you to process array elements one by one or all together.

- **Input**: JSON list (from JSONKeyExtractor or any JSON source)
- **Mode**: 
  - `"single"`: Extract one item by index
  - `"all"`: Output all items as a list
- **Index**: Integer specifying which item to extract (0-based, only used when mode is "single")
- **Output**: 
  - In `"single"` mode: The item at the specified index, plus the index value
  - In `"all"` mode: All items as a list, plus index value of -1
- **Category**: VTUtil

**Use Cases:**
- **Single mode**: When you have a list like the `scenes` array and want to extract individual scene objects for processing
- **All mode**: When you want to get all items from a list at once for batch processing

**Examples:**
- **Single mode:**
  - Extract first scene: Mode `"single"`, Index `0` → Returns first scene object
  - Extract second scene: Mode `"single"`, Index `1` → Returns second scene object
  - Extract last scene: Mode `"single"`, Index `-1` → Returns last scene object (Python-style negative indexing)
- **All mode:**
  - Get all scenes: Mode `"all"` → Returns the entire scenes array as a list

**Workflow Patterns:**
1. **Single item processing:**
   - Use `TextToJSON` to parse your JSON text
   - Use `JSONKeyExtractor` with path `"scenes"` to extract the scenes array
   - Use `JSONListIterator` with mode `"single"` and index `0`, `1`, `2`, etc. to get individual scenes
   - Process each scene object in subsequent nodes

2. **All items processing:**
   - Use `TextToJSON` to parse your JSON text
   - Use `JSONKeyExtractor` with path `"scenes"` to extract the scenes array
   - Use `JSONListIterator` with mode `"all"` to get all scenes as a list
   - Process all scenes together in subsequent nodes

**Error Handling:**
- If index is out of range (single mode), returns an error object with list length information
- If input is not a list, returns an error object explaining the issue
- In "all" mode, non-list inputs are wrapped in a list

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

