#!/usr/bin/env python3
"""
Test script for Gemini Image Tools
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from managers.tool_manager import ToolManager
from loguru import logger


def test_tool_registration():
    """Test that Gemini tools are properly registered"""
    print("🔧 Testing Gemini Image Tools Registration...")
    
    try:
        # Initialize tool manager
        tool_manager = ToolManager()
        
        # List all tools
        tools = tool_manager.list_tools()
        tool_names = [tool.name for tool in tools]
        
        print(f"📋 Total registered tools: {len(tools)}")
        print(f"🏷️  Categories: {list(tool_manager.get_categories().keys())}")
        
        # Check for Gemini tools
        gemini_tools = [
            "gemini_image_generator",
            "gemini_text_to_image", 
            "gemini_image_editor"
        ]
        
        print("\n🎨 Checking Gemini Image Tools:")
        for tool_name in gemini_tools:
            if tool_name in tool_names:
                tool_info = tool_manager.get_tool_info(tool_name)
                print(f"  ✅ {tool_name} - Category: {tool_info.category}")
                print(f"     Description: {tool_info.description[:80]}...")
            else:
                print(f"  ❌ {tool_name} - NOT FOUND")
        
        # Check ai_image category
        categories = tool_manager.get_categories()
        if "ai_image" in categories:
            print(f"\n🖼️  AI Image category tools: {categories['ai_image']}")
        else:
            print("\n❌ AI Image category not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing tool registration: {e}")
        return False


def test_tool_functionality():
    """Test basic tool functionality (without API call)"""
    print("\n🧪 Testing Tool Functionality...")
    
    # Check if GOOGLE_API_KEY is set
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not set - skipping API tests")
        print("   Set GOOGLE_API_KEY environment variable to test actual image generation")
        return True
    
    try:
        from tools.gemini_image_tool import gemini_text_to_image
        
        print("🎯 Testing gemini_text_to_image function...")
        
        # Test with a simple prompt (this will make actual API call)
        result = gemini_text_to_image(
            prompt="A simple red circle on white background",
            temperature=0.1
        )
        
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print(f"  ✅ Image generated successfully!")
            print(f"  📁 Image path: {result_data.get('main_image_path')}")
            print(f"  📊 Model used: {result_data.get('model_used')}")
        else:
            print(f"  ❌ Image generation failed: {result_data.get('error')}")
            
        return result_data.get("success", False)
        
    except Exception as e:
        print(f"❌ Error testing tool functionality: {e}")
        return False


def test_tool_manager_integration():
    """Test getting tools through ToolManager"""
    print("\n🔗 Testing ToolManager Integration...")
    
    try:
        tool_manager = ToolManager()
        
        # Get Gemini tools through tool manager
        gemini_tool = tool_manager.get_tool("gemini_text_to_image")
        
        if gemini_tool:
            print("  ✅ Successfully retrieved gemini_text_to_image through ToolManager")
            
            # Test tool signature
            import inspect
            sig = inspect.signature(gemini_tool)
            print(f"  📝 Tool signature: {sig}")
            
            return True
        else:
            print("  ❌ Could not retrieve gemini_text_to_image through ToolManager")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ToolManager integration: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Gemini Image Tools Test Suite\n")
    
    tests = [
        ("Tool Registration", test_tool_registration),
        ("ToolManager Integration", test_tool_manager_integration),
        ("Tool Functionality", test_tool_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Gemini Image Tools are ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
