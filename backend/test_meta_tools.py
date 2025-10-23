#!/usr/bin/env python3
"""
Test script for Meta Publisher Tools
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import the tools
from tools.meta_publisher_tool import (
    meta_get_account_info,
    meta_publish_text,
    meta_publish_image,
    meta_publish_text_and_image,
    meta_publish_content
)

def test_account_info():
    """Test getting account information"""
    print("🔍 Testing Meta account information...")
    try:
        result = meta_get_account_info()
        print(f"✅ Account info result:")
        print(f"   Success: {result['success']}")
        print(f"   Facebook: {result['facebook']['name']} (Status: {result['facebook']['status']})")
        print(f"   Instagram: @{result['instagram']['username']} (Status: {result['instagram']['status']})")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"❌ Account info test failed: {e}")
        return False

def test_text_publishing():
    """Test text publishing to Facebook"""
    print("\n📝 Testing text publishing...")
    try:
        result = meta_publish_text(
            text_message="🤖 Test post from Meta Publisher Tool! This is a test of the automated posting system.",
            platforms=["facebook"]  # Only Facebook since Instagram requires images
        )
        print(f"✅ Text publishing result:")
        print(f"   Success: {result['success']}")
        print(f"   Summary: {result['summary']}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        if 'facebook' in result['results']:
            fb_result = result['results']['facebook']
            if 'id' in fb_result:
                print(f"   Facebook Post ID: {fb_result['id']}")
        return result['success']
    except Exception as e:
        print(f"❌ Text publishing test failed: {e}")
        return False

def test_image_publishing():
    """Test image publishing with a sample image"""
    print("\n🖼️ Testing image publishing...")
    try:
        # Use a sample image URL (you can replace with your own)
        sample_image_url = "https://picsum.photos/800/600?random=1"
        
        result = meta_publish_image(
            image_url=sample_image_url,
            caption="🎨 Test image post from Meta Publisher Tool! This is an automated test.",
            platforms=["facebook", "instagram"]
        )
        print(f"✅ Image publishing result:")
        print(f"   Success: {result['success']}")
        print(f"   Summary: {result['summary']}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        
        for platform in ['facebook', 'instagram']:
            if platform in result['results']:
                platform_result = result['results'][platform]
                if 'id' in platform_result:
                    print(f"   {platform.title()} Post ID: {platform_result['id']}")
                elif 'error' in platform_result:
                    print(f"   {platform.title()} Error: {platform_result['error']['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ Image publishing test failed: {e}")
        return False

def test_universal_publishing():
    """Test the universal publishing function"""
    print("\n🚀 Testing universal publishing function...")
    try:
        result = meta_publish_content(
            content_type="text_with_image",
            text_message="🌟 Universal Meta Publisher Test! This post was created using the universal publishing function.",
            image_url="https://picsum.photos/800/600?random=2",
            platforms=["facebook", "instagram"]
        )
        print(f"✅ Universal publishing result:")
        print(f"   Success: {result['success']}")
        print(f"   Summary: {result['summary']}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        
        for platform in ['facebook', 'instagram']:
            if platform in result['results']:
                platform_result = result['results'][platform]
                if 'id' in platform_result:
                    print(f"   {platform.title()} Post ID: {platform_result['id']}")
                elif 'error' in platform_result:
                    print(f"   {platform.title()} Error: {platform_result['error']['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ Universal publishing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Meta Publisher Tools Test Suite")
    print("=" * 50)
    
    tests = [
        ("Account Info", test_account_info),
        ("Text Publishing", test_text_publishing),
        ("Image Publishing", test_image_publishing),
        ("Universal Publishing", test_universal_publishing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Meta Publisher Tools are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
