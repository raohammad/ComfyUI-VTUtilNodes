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

Converts text input to formatted JSON output.

- **Input**: Text string (can be valid or invalid JSON)
- **Output**: JSON string (formatted with indentation)
- **Category**: VTUtil

If the input text is valid JSON, it will be parsed and reformatted. If the input is invalid JSON, the output will be a JSON object containing error information.

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

