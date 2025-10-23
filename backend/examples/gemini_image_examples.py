#!/usr/bin/env python3
"""
Example usage of Gemini Image Tools
Demonstrates how to use the tools through the ToolManager
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from managers.tool_manager import ToolManager
from loguru import logger


def example_1_simple_text_to_image():
    """Example 1: Simple text-to-image generation"""
    print("🎨 Example 1: Simple Text-to-Image Generation")
    print("-" * 50)
    
    try:
        # Initialize tool manager
        tool_manager = ToolManager()
        
        # Get the simple text-to-image tool
        text_to_image_tool = tool_manager.get_tool("gemini_text_to_image")
        
        if not text_to_image_tool:
            print("❌ Tool not found. Make sure the tools are properly registered.")
            return
        
        # Generate an image
        result = text_to_image_tool(
            prompt="A cute orange tabby cat with bright green eyes, sitting on a comfortable blue velvet couch in a cozy living room with warm lighting",
            temperature=0.6,
            output_filename="cute_cat_example.png"
        )
        
        # Parse and display result
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f"✅ Image generated successfully!")
            print(f"📁 Image saved to: {result_data['main_image_path']}")
            print(f"🤖 Model used: {result_data['model_used']}")
            print(f"📊 Total images: {result_data['total_images']}")
        else:
            print(f"❌ Generation failed: {result_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in example 1: {e}")


def example_2_advanced_generation():
    """Example 2: Advanced image generation with custom settings"""
    print("\n🚀 Example 2: Advanced Image Generation")
    print("-" * 50)
    
    try:
        tool_manager = ToolManager()
        advanced_tool = tool_manager.get_tool("gemini_image_generator")
        
        if not advanced_tool:
            print("❌ Advanced tool not found.")
            return
        
        # Generate a more complex image
        result = advanced_tool(
            prompt="A futuristic cyberpunk cityscape at night with neon lights, flying cars, and towering skyscrapers. The scene should have a purple and blue color scheme with dramatic lighting and rain effects.",
            generation_type="text_to_image",
            model_id="gemini-2.5-flash-image-preview",
            temperature=0.8,
            output_filename="cyberpunk_city.png"
        )
        
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f"✅ Advanced image generated!")
            print(f"📁 Image path: {result_data['main_image_path']}")
            print(f"🎯 Generation type: {result_data['generation_type']}")
            print(f"🌡️  Temperature used: 0.8 (high creativity)")
            
            # Check for additional images
            if result_data.get("additional_images"):
                print(f"🎨 Additional variants: {len(result_data['additional_images'])}")
        else:
            print(f"❌ Generation failed: {result_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in example 2: {e}")


def example_3_image_editing():
    """Example 3: Image editing (requires existing image)"""
    print("\n✏️  Example 3: Image Editing")
    print("-" * 50)
    
    try:
        tool_manager = ToolManager()
        editor_tool = tool_manager.get_tool("gemini_image_editor")
        
        if not editor_tool:
            print("❌ Editor tool not found.")
            return
        
        # Check if we have a generated image to edit
        generated_images_dir = Path("generated_images")
        if not generated_images_dir.exists():
            print("⚠️  No generated_images directory found. Run example 1 first to create an image to edit.")
            return
        
        # Find the first PNG image in the directory
        image_files = list(generated_images_dir.glob("*.png"))
        if not image_files:
            print("⚠️  No images found to edit. Run example 1 first to create an image.")
            return
        
        input_image = str(image_files[0])
        print(f"📷 Using image for editing: {input_image}")
        
        # Edit the image
        result = editor_tool(
            prompt="Change the scene to be during a beautiful sunset with warm golden lighting. Keep all the main subjects but add a magical, dreamy atmosphere.",
            input_image_path=input_image,
            temperature=0.5,
            output_filename="edited_sunset_scene.png"
        )
        
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f"✅ Image edited successfully!")
            print(f"📁 Edited image: {result_data['main_image_path']}")
            print(f"🔄 Original: {input_image}")
        else:
            print(f"❌ Editing failed: {result_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in example 3: {e}")


def example_4_list_available_tools():
    """Example 4: List all available Gemini tools"""
    print("\n📋 Example 4: Available Gemini Tools")
    print("-" * 50)
    
    try:
        tool_manager = ToolManager()
        
        # Get all tools in ai_image category
        categories = tool_manager.get_categories()
        ai_image_tools = categories.get("ai_image", [])
        
        print(f"🎨 AI Image Tools ({len(ai_image_tools)} available):")
        
        for tool_name in ai_image_tools:
            tool_info = tool_manager.get_tool_info(tool_name)
            if tool_info:
                print(f"\n  🔧 {tool_name}")
                print(f"     📝 {tool_info.description[:80]}...")
                print(f"     👤 Author: {tool_info.author}")
                print(f"     📊 Usage count: {tool_info.usage_count}")
                print(f"     ✅ Enabled: {tool_info.is_enabled}")
        
        # Show total tool count
        all_tools = tool_manager.list_tools()
        print(f"\n📊 Total tools registered: {len(all_tools)}")
        print(f"🏷️  Categories: {list(categories.keys())}")
        
    except Exception as e:
        print(f"❌ Error in example 4: {e}")


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites")
    print("-" * 50)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print("✅ GOOGLE_API_KEY is set")
    else:
        print("❌ GOOGLE_API_KEY not set")
        print("   Please set your Google API key:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        return False
    
    # Check dependencies
    try:
        import google.genai
        print("✅ google-genai package available")
    except ImportError:
        print("❌ google-genai package not found")
        print("   Install with: pip install google-genai")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL) package available")
    except ImportError:
        print("❌ Pillow package not found")
        print("   Install with: pip install Pillow")
        return False
    
    # Check output directory
    output_dir = Path("generated_images")
    if output_dir.exists():
        print(f"✅ Output directory exists: {output_dir}")
    else:
        print(f"📁 Output directory will be created: {output_dir}")
    
    return True


def main():
    """Run all examples"""
    print("🎨 Gemini Image Tools Examples")
    print("=" * 60)
    
    # Check prerequisites first
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        return
    
    print("\n🚀 Running Examples...")
    
    # Run examples
    examples = [
        ("List Available Tools", example_4_list_available_tools),
        ("Simple Text-to-Image", example_1_simple_text_to_image),
        ("Advanced Generation", example_2_advanced_generation),
        ("Image Editing", example_3_image_editing),
    ]
    
    for example_name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Example '{example_name}' failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Examples completed!")
    print("\n💡 Tips:")
    print("   - Check the generated_images/ directory for output files")
    print("   - Each image has a corresponding .json metadata file")
    print("   - Adjust temperature values for different creativity levels")
    print("   - Use specific prompts for better results")


if __name__ == "__main__":
    main()
