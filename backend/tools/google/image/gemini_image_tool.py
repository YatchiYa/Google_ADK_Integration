"""
Google Gemini Image Generation Tool for Google ADK Integration
Function-based tool for generating and editing images using Google Gemini AI
"""

import base64
import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from io import BytesIO

from google import genai
from PIL import Image
from loguru import logger


# Configuration constants
GEMINI_CONFIG = {
    "models": [
        "gemini-2.5-flash-image-preview",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ],
    "generation_types": [
        "text_to_image",
        "image_editing",
        "image_restoration",
        "image_colorization",
        "iterative_editing"
    ]
}

# Global output directory
OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _validate_gemini_params(
    generation_type: str,
    model_id: str,
    temperature: float,
    input_image_path: Optional[str] = None,
) -> None:
    """Validate Gemini parameters."""
    if model_id not in GEMINI_CONFIG["models"]:
        raise ValueError(f"Invalid model_id. Must be one of: {GEMINI_CONFIG['models']}")
    
    if generation_type not in GEMINI_CONFIG["generation_types"]:
        raise ValueError(f"Invalid generation_type. Must be one of: {GEMINI_CONFIG['generation_types']}")
    
    if not 0.0 <= temperature <= 2.0:
        raise ValueError("temperature must be between 0.0 and 2.0")
    
    # Check if input image is required for certain operations
    if generation_type in ["image_editing", "image_restoration", "image_colorization"] and not input_image_path:
        raise ValueError(f"input_image_path is required for generation_type: {generation_type}")
    
    # Validate input image exists if provided
    if input_image_path and not Path(input_image_path).exists():
        raise ValueError(f"Input image not found: {input_image_path}")


def _load_image(image_path: str) -> Image.Image:
    """Load image from path."""
    try:
        return Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Failed to load image from {image_path}: {e}")


def _save_image(image: Image.Image, filename: str) -> Path:
    """Save PIL image to file."""
    file_path = "/tmp/generated_images/" + filename
    image.save(file_path)
    logger.info(f"Image saved successfully at: {file_path}")
    return file_path


def _image_to_base64(image: Image.Image) -> str:
    """Convert PIL image to base64 string."""
    try:
        buffer = BytesIO()
        # Save as PNG to preserve quality
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_data = buffer.getvalue()
        base64_string = base64.b64encode(image_data).decode('utf-8') 
        return f"data:image/png;base64,{base64_string}"
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        return ""


def _save_metadata(metadata: Dict[str, Any], filepath: Path) -> None:
    """Save image metadata to JSON file."""
    try:
        metadata_path = filepath.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved successfully at: {metadata_path}")
    except Exception as e:
        logger.error(f"Error saving metadata: {e}")
        raise


def _generate_filename(generation_type: str, custom_filename: Optional[str] = None) -> str:
    """Generate filename for output image."""
    if custom_filename:
        # Ensure it has .png extension
        if not custom_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            custom_filename += '.png'
        return custom_filename
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"gemini_{generation_type}_{timestamp}.png"


def gemini_image_generator(
    prompt: str,
    generation_type: str = "text_to_image",
    input_image_path: Optional[str] = None,
    additional_image_paths: Optional[str] = None,
    model_id: str = "gemini-2.5-flash-image-preview",
    temperature: float = 0.4,
    output_filename: Optional[str] = None,
) -> str:
    """
    Generate and edit images using Google Gemini AI.
    
    Features:
    1. Text-to-image generation
    2. Image editing with text prompts
    3. Image restoration and colorization
    4. Multiple image composition
    5. Iterative image editing
    
    Args:
        prompt: Describe what you want in the image or how to edit it. Tips:
                - Be specific about subject, style, lighting
                - For editing: describe the changes you want
                - For restoration: mention the type of restoration needed
                - Include mood and atmosphere descriptions
        generation_type: Type of image generation:
                        - text_to_image: Generate new image from text
                        - image_editing: Edit existing image with text prompt
                        - image_restoration: Restore and enhance old images
                        - image_colorization: Add color to black and white images
                        - iterative_editing: Multiple edits in sequence
        input_image_path: Path to input image (required for editing operations)
        additional_image_paths: Comma-separated paths to additional images for multi-image operations
        model_id: The Gemini model to use (default: gemini-2.5-flash-image-preview)
        temperature: Controls creativity (0.0-2.0). Lower = more focused, higher = more creative
        output_filename: Custom filename for output image (optional)
        
    Returns:
        str: JSON string with image paths and metadata
    """
    try:
        logger.info(f"Starting Gemini image generation - Type: {generation_type}, Model: {model_id}")
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Validate parameters
        _validate_gemini_params(generation_type, model_id, temperature, input_image_path)
        
        # Initialize Google Gemini client
        gemini_client = genai.Client(api_key=api_key)
        logger.debug(f"Initialized Gemini client with API key")
        
        # Prepare content list for API call
        contents = [prompt]
        
        # Add input image if provided
        if input_image_path:
            input_image = _load_image(input_image_path)
            contents.append(input_image)
            logger.debug(f"Added input image: {input_image_path}")
        
        # Add additional images if provided
        if additional_image_paths:
            additional_paths = [path.strip() for path in additional_image_paths.split(',')]
            for path in additional_paths:
                if path and Path(path).exists():
                    additional_image = _load_image(path)
                    contents.append(additional_image)
                    logger.debug(f"Added additional image: {path}")
        
        logger.info(f"Generating image with Gemini - Type: {generation_type}, Model: {model_id}")
        
        # Generate content with Gemini
        response = gemini_client.models.generate_content(
            model=model_id,
            contents=contents,
        )
        
        # Process response to find and save images
        generated_images = []
        text_responses = []
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_responses.append(part.text)
                logger.info(f"Gemini text response: {part.text}")
            elif part.inline_data is not None:
                # Convert inline data to PIL Image
                image = Image.open(BytesIO(part.inline_data.data))
                generated_images.append(image)
        
        if not generated_images:
            raise ValueError("No images were generated in the response")
        
        logger.info(f"Generated {len(generated_images)} images")
        
        # Save the first (or main) generated image
        filename = _generate_filename(generation_type, output_filename)
        file_path = _save_image(generated_images[0], filename)
        
        # Save additional images if multiple were generated
        additional_paths = []
        for i, img in enumerate(generated_images[1:], 1):
            additional_filename = f"{Path(filename).stem}_variant_{i}.png"
            additional_path = _save_image(img, additional_filename)
            additional_paths.append(str(additional_path))
        
        # Save metadata
        metadata = {
            "filename": filename,
            "timestamp": datetime.datetime.now().isoformat(),
            "model_id": model_id,
            "prompt": prompt,
            "generation_type": generation_type,
            "temperature": temperature,
            "input_image_path": input_image_path,
            "additional_image_paths": additional_image_paths,
            "local_path": str(file_path),
            "additional_generated_paths": additional_paths,
            "text_responses": text_responses,
            "total_images_generated": len(generated_images),
        }
        _save_metadata(metadata, file_path)
        
        # result_info = {
        #     "success": True,
        #     "main_image_path": str(file_path),
        #     "main_image_filename": file_path.name,
        #     "main_image_url": f"/api/v1/images/serve/{file_path.name}",
        #     "additional_images": additional_paths,
        #     "text_responses": text_responses,
        #     "total_images": len(generated_images),
        #     "generation_type": generation_type,
        #     "model_used": model_id,
        #     "prompt": prompt,
        #     "metadata_path": str(file_path.with_suffix('.json'))
        # }
        return str(file_path)
        
        # logger.info(f"Successfully generated {len(generated_images)} images. Main image: {file_path}")
        # return json.dumps(result_info, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating image with Gemini: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "generation_type": generation_type,
            "model_used": model_id,
            "prompt": prompt
        }
        return json.dumps(error_result, indent=2)


def gemini_text_to_image(
    prompt: str,
    model_id: str = "gemini-2.5-flash-image-preview",
    temperature: float = 0.4,
    output_filename: Optional[str] = None,
) -> str:
    """
    Simple text-to-image generation using Google Gemini AI.
    
    Args:
        prompt: Text description of the image to generate
        model_id: The Gemini model to use
        temperature: Controls creativity (0.0-2.0)
        output_filename: Custom filename for output image
        
    Returns:
        str: JSON string with image path and metadata
    """
    return gemini_image_generator(
        prompt=prompt,
        generation_type="text_to_image",
        model_id=model_id,
        temperature=temperature,
        output_filename=output_filename
    )


def gemini_image_editor(
    prompt: str,
    input_image_path: str,
    model_id: str = "gemini-2.5-flash-image-preview",
    temperature: float = 0.4,
    output_filename: Optional[str] = None,
) -> str:
    """
    Edit existing images using Google Gemini AI.
    
    Args:
        prompt: Description of the edits to make
        input_image_path: Path to the image to edit
        model_id: The Gemini model to use
        temperature: Controls creativity (0.0-2.0)
        output_filename: Custom filename for output image
        
    Returns:
        str: JSON string with edited image path and metadata
    """
    return gemini_image_generator(
        prompt=prompt,
        generation_type="image_editing",
        input_image_path=input_image_path,
        model_id=model_id,
        temperature=temperature,
        output_filename=output_filename
    )


if __name__ == "__main__":
    # Test the tool
    test_result = gemini_text_to_image(
        prompt="Create a photorealistic image of an orange cat with green eyes, sitting on a couch",
        temperature=0.6
    )
    print("Test result:")
    print(test_result)
