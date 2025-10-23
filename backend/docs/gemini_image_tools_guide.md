# Google Gemini Image Tools Guide

This guide explains how to use the Google Gemini Image Generation tools that have been integrated into your Google ADK Integration system.

## Overview

The Gemini Image Tools provide powerful AI-driven image generation and editing capabilities using Google's Gemini AI models. These tools have been transformed from a class-based implementation to function-based tools that integrate seamlessly with your ToolManager system.

## Available Tools

### 1. `gemini_image_generator` (Advanced Tool)
The most comprehensive tool that supports all image generation types.

**Parameters:**
- `prompt` (required): Text description for generation or editing instructions
- `generation_type` (optional): Type of operation (`text_to_image`, `image_editing`, `image_restoration`, `image_colorization`, `iterative_editing`)
- `input_image_path` (optional): Path to input image for editing operations
- `additional_image_paths` (optional): Comma-separated paths for multi-image operations
- `model_id` (optional): Gemini model to use (default: `gemini-2.5-flash-image-preview`)
- `temperature` (optional): Creativity control (0.0-2.0, default: 0.4)
- `output_filename` (optional): Custom filename for output

### 2. `gemini_text_to_image` (Simple Tool)
Simplified tool for basic text-to-image generation.

**Parameters:**
- `prompt` (required): Text description of the image to generate
- `model_id` (optional): Gemini model to use
- `temperature` (optional): Creativity control (0.0-2.0)
- `output_filename` (optional): Custom filename for output

### 3. `gemini_image_editor` (Editing Tool)
Specialized tool for editing existing images.

**Parameters:**
- `prompt` (required): Description of the edits to make
- `input_image_path` (required): Path to the image to edit
- `model_id` (optional): Gemini model to use
- `temperature` (optional): Creativity control (0.0-2.0)
- `output_filename` (optional): Custom filename for output

## Setup Requirements

### 1. Environment Variable
Set your Google API key:
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
```

### 2. Dependencies
Ensure these packages are installed:
```bash
pip install google-genai Pillow loguru
```

### 3. Output Directory
Images are saved to `generated_images/` directory (created automatically).

## Usage Examples

### Example 1: Simple Text-to-Image
```python
from managers.tool_manager import ToolManager

tool_manager = ToolManager()
text_to_image_tool = tool_manager.get_tool("gemini_text_to_image")

result = text_to_image_tool(
    prompt="A photorealistic orange cat with green eyes sitting on a blue couch",
    temperature=0.6
)

print(result)  # JSON with image path and metadata
```

### Example 2: Advanced Image Generation
```python
advanced_tool = tool_manager.get_tool("gemini_image_generator")

result = advanced_tool(
    prompt="Create a futuristic cityscape at sunset with flying cars",
    generation_type="text_to_image",
    model_id="gemini-2.5-flash-image-preview",
    temperature=0.8,
    output_filename="futuristic_city.png"
)
```

### Example 3: Image Editing
```python
editor_tool = tool_manager.get_tool("gemini_image_editor")

result = editor_tool(
    prompt="Change the cat to a golden retriever, keep everything else the same",
    input_image_path="/path/to/original/image.jpg",
    temperature=0.4
)
```

### Example 4: Multi-Image Composition
```python
result = advanced_tool(
    prompt="Combine these images into a collage with a nature theme",
    generation_type="iterative_editing",
    input_image_path="/path/to/image1.jpg",
    additional_image_paths="/path/to/image2.jpg,/path/to/image3.jpg"
)
```

## Response Format

All tools return a JSON string with the following structure:

```json
{
  "success": true,
  "main_image_path": "/path/to/generated_images/image.png",
  "additional_images": ["/path/to/variant1.png"],
  "text_responses": ["Generated successfully"],
  "total_images": 1,
  "generation_type": "text_to_image",
  "model_used": "gemini-2.5-flash-image-preview",
  "prompt": "Your original prompt",
  "metadata_path": "/path/to/image.json"
}
```

## Error Handling

If an error occurs, the response will include:

```json
{
  "success": false,
  "error": "Error description",
  "generation_type": "text_to_image",
  "model_used": "gemini-2.5-flash-image-preview",
  "prompt": "Your original prompt"
}
```

## Available Models

- `gemini-2.5-flash-image-preview` (default, best for image generation)
- `gemini-1.5-flash` (faster, good for simple tasks)
- `gemini-1.5-pro` (more capable, slower)

## Generation Types

- `text_to_image`: Generate new images from text descriptions
- `image_editing`: Edit existing images with text prompts
- `image_restoration`: Restore and enhance old or damaged images
- `image_colorization`: Add color to black and white images
- `iterative_editing`: Multiple edits in sequence

## Tips for Better Results

### Prompt Writing
- Be specific about subject, style, and lighting
- Include mood and atmosphere descriptions
- For editing: clearly describe the changes you want
- For restoration: mention the type of restoration needed

### Temperature Settings
- **0.0-0.3**: Very focused, consistent results
- **0.4-0.7**: Balanced creativity and consistency (recommended)
- **0.8-1.0**: More creative and varied results
- **1.1-2.0**: Highly creative, potentially unpredictable

### File Management
- Images are automatically saved with timestamps
- Metadata is saved as JSON files alongside images
- Multiple variants are saved with `_variant_N` suffixes
- Custom filenames are supported

## Integration with Agents

These tools are automatically registered in the `ai_image` category and can be attached to any agent through the ToolManager:

```python
# In your agent configuration
agent_tools = tool_manager.get_tools_for_agent([
    "gemini_text_to_image",
    "gemini_image_editor"
])
```

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY environment variable is required"**
   - Set the environment variable with your Google API key

2. **"Invalid model_id"**
   - Use one of the supported models listed above

3. **"Input image not found"**
   - Verify the image path exists and is accessible

4. **"No images were generated"**
   - Check your prompt and try adjusting the temperature
   - Verify your API key has image generation permissions

### Logging
The tools use loguru for logging. Check the logs for detailed error information and debugging.

## File Structure

```
backend/
├── tools/
│   └── gemini_image_tool.py          # Main tool implementation
├── managers/
│   └── tool_manager.py               # Tool registration
├── generated_images/                 # Output directory (auto-created)
│   ├── gemini_text_to_image_*.png   # Generated images
│   └── gemini_text_to_image_*.json  # Metadata files
└── docs/
    └── gemini_image_tools_guide.md  # This guide
```

## Next Steps

1. Set up your Google API key
2. Test the tools with simple prompts
3. Integrate with your agents
4. Experiment with different models and settings
5. Build custom workflows using the advanced features

The tools are now ready to use and will automatically be available to any agents that have them attached through the ToolManager system.
