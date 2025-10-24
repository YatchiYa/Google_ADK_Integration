"""
Meta Publisher Tool for Google ADK Integration
Allows publishing content to Facebook pages and Instagram accounts
"""

import json
import time
import requests
from typing import Dict, List, Optional, Union, Any
from loguru import logger

# Import your existing meta handler functions
from .meta_account_handler import (
    post_text_to_facebook_page,
    post_image_to_facebook_page,
    post_text_with_image_to_facebook_page,
    post_image_to_instagram_account,
    post_text_with_image_to_instagram_account,
    get_page_access_token,
    get_instagram_account_details
)

# Configuration - Your specific account IDs
FACEBOOK_PAGE_ID = "861883367002548"
INSTAGRAM_ACCOUNT_ID = "17841460715803093"

# Default access tokens (fallback - will be replaced by dynamic tokens from frontend)
ACCESS_TOKEN = "EAAGZAhN3OgkMBPzCrQ3EkneaZBlWdG0Q9oCeUbOkHK2WtpHLllkFCMJ1CEoytII2wgJSScJNsNLlZBp4TN6Al841VGzkeTA7DBeWTXnsyeBVZCFW30swM16XZAhvs57WfoT6mwjwfUOddMGBX5KP6eXZBgkv9MgmFxBzSuJQSGHywIL81dThyjOgAx3iJn3QjGJucxZBj6e9lNZBflul81L01NRZBSI6lMu4ZCh6i5xagPsdVffSILfpbKQleo8NYjRJ1BtgafM9yEruKO7kqj"
FACEBOOK_PAGE_ACCESS_TOKEN = "EAAGZAhN3OgkMBPzCrQ3EkneaZBlWdG0Q9oCeUbOkHK2WtpHLllkFCMJ1CEoytII2wgJSScJNsNLlZBp4TN6Al841VGzkeTA7DBeWTXnsyeBVZCFW30swM16XZAhvs57WfoT6mwjwfUOddMGBX5KP6eXZBgkv9MgmFxBzSuJQSGHywIL81dThyjOgAx3iJn3QjGJucxZBj6e9lNZBflul81L01NRZBSI6lMu4ZCh6i5xagPsdVffSILfpbKQleo8NYjRJ1BtgafM9yEruKO7kqj"

# Dynamic token storage (updated from frontend)
_dynamic_tokens = {
    "user_access_token": None,
    "page_access_token": None,
    "page_id": None,
    "instagram_account_id": None,
    "last_updated": None
}

def update_meta_tokens(
    user_access_token: str,
    page_access_token: str,
    page_id: str,
    instagram_account_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update Meta authentication tokens from frontend.
    
    Args:
        user_access_token: Facebook user access token
        page_access_token: Facebook page access token
        page_id: Facebook page ID
        instagram_account_id: Instagram business account ID (optional)
        
    Returns:
        Dict containing update status
        
    Example:
        result = update_meta_tokens(
            user_access_token="user_token",
            page_access_token="page_token", 
            page_id="123456789",
            instagram_account_id="ig_123456"
        )
    """
    global _dynamic_tokens
    
    try:
        _dynamic_tokens.update({
            "user_access_token": user_access_token,
            "page_access_token": page_access_token,
            "page_id": page_id,
            "instagram_account_id": instagram_account_id or INSTAGRAM_ACCOUNT_ID,
            "last_updated": time.time()
        })
        
        logger.info(f"✅ Meta tokens updated successfully")
        logger.info(f"   Page ID: {page_id}")
        logger.info(f"   Instagram ID: {instagram_account_id}")
        
        return {
            "success": True,
            "message": "Meta tokens updated successfully",
            "page_id": page_id,
            "instagram_account_id": instagram_account_id,
            "updated_at": _dynamic_tokens["last_updated"]
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to update Meta tokens: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update Meta tokens"
        }

def get_active_tokens() -> Dict[str, str]:
    """
    Get currently active tokens (dynamic if available, fallback to static).
    
    Returns:
        Dict containing active tokens
    """
    if _dynamic_tokens["page_access_token"] and _dynamic_tokens["last_updated"]:
        # Check if tokens are not too old (24 hours)
        if time.time() - _dynamic_tokens["last_updated"] < 86400:
            return {
                "page_access_token": _dynamic_tokens["page_access_token"],
                "page_id": _dynamic_tokens["page_id"],
                "instagram_account_id": _dynamic_tokens["instagram_account_id"]
            }
    
    # Fallback to static tokens
    return {
        "page_access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
        "page_id": FACEBOOK_PAGE_ID,
        "instagram_account_id": INSTAGRAM_ACCOUNT_ID
    }

def meta_publish_content(
    content_type: str,
    text_message: str,
    image_url: str,
    platforms: List[str],
    facebook_page_id: Optional[str] = None,
    instagram_account_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Universal Meta publishing tool for Facebook and Instagram.
    
    Args:
        content_type: Type of content ("text", "image", "text_with_image")
        text_message: Text content to publish
        image_url: URL of image to publish (must be publicly accessible)
        platforms: List of platforms to publish to ("facebook", "instagram", or both)
        facebook_page_id: Facebook page ID (defaults to your page)
        instagram_account_id: Instagram account ID (defaults to your account)
        
    Returns:
        Dict containing publishing results for each platform
        
    Examples:
        # Text only to Facebook
        result = meta_publish_content(
            content_type="text",
            text_message="Hello from AI! 🤖",
            platforms=["facebook"]
        )
        
        # Image with caption to both platforms
        result = meta_publish_content(
            content_type="text_with_image",
            text_message="Check out this amazing AI-generated image! 🎨",
            image_url="https://example.com/image.jpg",
            platforms=["facebook", "instagram"]
        )
        
        # Image only to Instagram
        result = meta_publish_content(
            content_type="image",
            image_url="https://example.com/photo.jpg",
            platforms=["instagram"]
        )
    """
    # Handle default values
    if facebook_page_id is None:
        facebook_page_id = FACEBOOK_PAGE_ID
    if instagram_account_id is None:
        instagram_account_id = INSTAGRAM_ACCOUNT_ID
    
    logger.info(f"🚀 Meta Publisher Tool called with:")
    logger.info(f"   Content Type: {content_type}")
    logger.info(f"   Text: {text_message[:100]}{'...' if len(text_message) > 100 else ''}")
    logger.info(f"   Image URL: {image_url}")
    logger.info(f"   Platforms: {platforms}")
    
    results = {
        "success": True,
        "platforms_attempted": platforms,
        "results": {},
        "errors": [],
        "summary": ""
    }
    
    # Validate inputs
    if not platforms:
        results["success"] = False
        results["errors"].append("No platforms specified")
        return results
    
    if content_type not in ["text", "image", "text_with_image"]:
        results["success"] = False
        results["errors"].append(f"Invalid content_type: {content_type}")
        return results
    
    if content_type in ["image", "text_with_image"] and not image_url:
        results["success"] = False
        results["errors"].append("Image URL required for image content")
        return results
    
    if content_type in ["text", "text_with_image"] and not text_message:
        results["success"] = False
        results["errors"].append("Text message required for text content")
        return results
    
    # Publish to Facebook
    if "facebook" in platforms:
        logger.info("📘 Publishing to Facebook...")
        try:
            fb_result = _publish_to_facebook(
                content_type=content_type,
                text_message=text_message,
                image_url=image_url,
                page_id=facebook_page_id
            )
            results["results"]["facebook"] = fb_result
            
            if "error" in fb_result:
                results["errors"].append(f"Facebook: {fb_result['error'].get('message', 'Unknown error')}")
            else:
                logger.info(f"✅ Facebook post successful: {fb_result.get('id', 'N/A')}")
                
        except Exception as e:
            error_msg = f"Facebook publishing failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["results"]["facebook"] = {"error": {"message": str(e)}}
    
    # Publish to Instagram
    if "instagram" in platforms:
        logger.info("📷 Publishing to Instagram...")
        try:
            ig_result = _publish_to_instagram(
                content_type=content_type,
                text_message=text_message,
                image_url=image_url,
                instagram_id=instagram_account_id
            )
            results["results"]["instagram"] = ig_result
            
            if "error" in ig_result:
                results["errors"].append(f"Instagram: {ig_result['error'].get('message', 'Unknown error')}")
            else:
                logger.info(f"✅ Instagram post successful: {ig_result.get('id', 'N/A')}")
                
        except Exception as e:
            error_msg = f"Instagram publishing failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["results"]["instagram"] = {"error": {"message": str(e)}}
    
    # Update success status
    if results["errors"]:
        results["success"] = False
    
    # Generate summary
    successful_platforms = []
    failed_platforms = []
    
    for platform in platforms:
        if platform in results["results"]:
            if "error" not in results["results"][platform]:
                successful_platforms.append(platform)
            else:
                failed_platforms.append(platform)
    
    if successful_platforms and not failed_platforms:
        results["summary"] = f"✅ Successfully published to {', '.join(successful_platforms)}"
    elif successful_platforms and failed_platforms:
        results["summary"] = f"⚠️ Published to {', '.join(successful_platforms)}, failed on {', '.join(failed_platforms)}"
    else:
        results["summary"] = f"❌ Failed to publish to all platforms: {', '.join(failed_platforms)}"
    
    logger.info(f"📊 Publishing complete: {results['summary']}")
    return results

def _publish_to_facebook(content_type: str, text_message: str, image_url: str, page_id: str) -> Dict:
    """Internal function to publish content to Facebook page"""
    logger.info(f"📘 Facebook publishing: {content_type}")
    
    try:
        # Get active tokens
        tokens = get_active_tokens()
        page_access_token = tokens["page_access_token"]
        
        if content_type == "text":
            return post_text_to_facebook_page(page_id, page_access_token, text_message)
        elif content_type == "image":
            return post_image_to_facebook_page(page_id, page_access_token, image_url, "")
        elif content_type == "text_with_image":
            return post_text_with_image_to_facebook_page(page_id, page_access_token, text_message, image_url)
        else:
            return {"error": {"message": f"Unsupported Facebook content type: {content_type}"}}
    except Exception as e:
        logger.error(f"Facebook publishing error: {e}")
        return {"error": {"message": str(e)}}

def _publish_to_instagram(content_type: str, text_message: str, image_url: str, instagram_id: str) -> Dict:
    """Internal function to publish content to Instagram account"""
    logger.info(f"📷 Instagram publishing: {content_type}")
    
    try:
        # Get active tokens
        tokens = get_active_tokens()
        page_access_token = tokens["page_access_token"]
        
        if content_type == "text":
            # Instagram typically requires images, but we'll try
            return {"error": {"message": "Instagram requires images for most posts. Use 'text_with_image' or 'image' instead."}}
        elif content_type == "image":
            return post_image_to_instagram_account(instagram_id, page_access_token, image_url, "")
        elif content_type == "text_with_image":
            return post_text_with_image_to_instagram_account(instagram_id, page_access_token, text_message, image_url)
        else:
            return {"error": {"message": f"Unsupported Instagram content type: {content_type}"}}
    except Exception as e:
        logger.error(f"Instagram publishing error: {e}")
        return {"error": {"message": str(e)}}

def meta_publish_text(
    text_message: str,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Simplified function to publish text content.
    Note: Instagram requires images, so this will only work for Facebook.
    
    Args:
        text_message: Text content to publish
        platforms: List of platforms ("facebook", "instagram")
        
    Returns:
        Dict containing publishing results
        
    Example:
        result = meta_publish_text("Hello from AI! 🤖", ["facebook"])
    """
    if platforms is None:
        platforms = ["facebook", "instagram"]
        
    return meta_publish_content(
        content_type="text",
        text_message=text_message,
        image_url="",
        platforms=platforms
    )

def meta_publish_image(
    image_url: str,
    caption: Optional[str] = None,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Simplified function to publish image content.
    
    Args:
        image_url: URL of image to publish
        caption: Optional caption for the image
        platforms: List of platforms ("facebook", "instagram")
        
    Returns:
        Dict containing publishing results
        
    Example:
        result = meta_publish_image(
            "https://example.com/image.jpg",
            "Amazing AI-generated art! 🎨",
            ["facebook", "instagram"]
        )
    """
    if caption is None:
        caption = ""
    if platforms is None:
        platforms = ["facebook", "instagram"]
        
    if caption:
        return meta_publish_content(
            content_type="text_with_image",
            text_message=caption,
            image_url=image_url,
            platforms=platforms
        )
    else:
        return meta_publish_content(
            content_type="image",
            text_message="",
            image_url=image_url,
            platforms=platforms
        )

def meta_publish_text_and_image(
    text_message: str,
    image_url: str,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Simplified function to publish text with image.
    
    Args:
        text_message: Text content to publish
        image_url: URL of image to publish
        platforms: List of platforms ("facebook", "instagram")
        
    Returns:
        Dict containing publishing results
        
    Example:
        result = meta_publish_text_and_image(
            "Check out this amazing view! 🌅",
            "https://example.com/sunset.jpg",
            ["facebook", "instagram"]
        )
    """
    if platforms is None:
        platforms = ["facebook", "instagram"]
        
    return meta_publish_content(
        content_type="text_with_image",
        text_message=text_message,
        image_url=image_url,
        platforms=platforms
    )

def meta_get_account_info() -> Dict[str, Any]:
    """
    Get information about configured Meta accounts.
    
    Returns:
        Dict containing account information and status
        
    Example:
        info = meta_get_account_info()
        print(f"Facebook Page: {info['facebook']['name']}")
        print(f"Instagram: @{info['instagram']['username']}")
    """
    logger.info("🔍 Getting Meta account information...")
    
    result = {
        "success": True,
        "facebook": {
            "page_id": FACEBOOK_PAGE_ID,
            "name": "Unknown",
            "status": "unknown"
        },
        "instagram": {
            "account_id": INSTAGRAM_ACCOUNT_ID,
            "username": "Unknown",
            "status": "unknown"
        },
        "errors": []
    }
    
    # Try to get Facebook page info
    try:
        from .meta_account_handler import get_specific_page_info
        fb_info = get_specific_page_info(FACEBOOK_PAGE_ID)
        if "error" not in fb_info:
            result["facebook"]["name"] = fb_info.get("name", "Unknown")
            result["facebook"]["category"] = fb_info.get("category", "Unknown")
            result["facebook"]["status"] = "active"
        else:
            result["errors"].append(f"Facebook: {fb_info['error'].get('message', 'Unknown error')}")
            result["facebook"]["status"] = "error"
    except Exception as e:
        result["errors"].append(f"Facebook info error: {str(e)}")
        result["facebook"]["status"] = "error"
    
    # Try to get Instagram account info
    try:
        ig_info = get_instagram_account_details(INSTAGRAM_ACCOUNT_ID, FACEBOOK_PAGE_ACCESS_TOKEN)
        if "error" not in ig_info:
            result["instagram"]["username"] = ig_info.get("username", "Unknown")
            result["instagram"]["name"] = ig_info.get("name", "Unknown")
            result["instagram"]["followers"] = ig_info.get("followers_count", 0)
            result["instagram"]["status"] = "active"
        else:
            result["errors"].append(f"Instagram: {ig_info['error'].get('message', 'Unknown error')}")
            result["instagram"]["status"] = "error"
    except Exception as e:
        result["errors"].append(f"Instagram info error: {str(e)}")
        result["instagram"]["status"] = "error"
    
    if result["errors"]:
        result["success"] = False
    
    logger.info(f"📊 Account info retrieved: {result['success']}")
    return result

# Tool registration functions for the ADK system
def get_meta_publisher_tools() -> List[Dict[str, Any]]:
    """
    Get list of Meta publisher tools for registration with the tool manager.
    
    Returns:
        List of tool definitions for the ADK system
    """
    return [
        {
            "name": "update_meta_tokens",
            "description": "Update Meta authentication tokens from frontend Facebook login.",
            "function": update_meta_tokens,
            "parameters": {
                "user_access_token": {
                    "type": "string",
                    "description": "Facebook user access token"
                },
                "page_access_token": {
                    "type": "string",
                    "description": "Facebook page access token"
                },
                "page_id": {
                    "type": "string",
                    "description": "Facebook page ID"
                },
                "instagram_account_id": {
                    "type": "string",
                    "description": "Instagram business account ID (optional)"
                }
            },
            "required": ["user_access_token", "page_access_token", "page_id"],
            "category": "social_media"
        },
        {
            "name": "meta_publish_content",
            "description": "Universal Meta publishing tool for Facebook and Instagram. Supports text, images, and combined content.",
            "function": meta_publish_content,
            "parameters": {
                "content_type": {
                    "type": "string",
                    "description": "Type of content to publish",
                    "enum": ["text", "image", "text_with_image"]
                },
                "text_message": {
                    "type": "string",
                    "description": "Text content to publish"
                },
                "image_url": {
                    "type": "string",
                    "description": "URL of image to publish (must be publicly accessible)"
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["facebook", "instagram"]},
                    "description": "List of platforms to publish to"
                }
            },
            "required": ["content_type", "text_message", "image_url", "platforms"],
            "category": "social_media"
        },
        {
            "name": "meta_publish_text",
            "description": "Publish text content to Facebook (Instagram requires images).",
            "function": meta_publish_text,
            "parameters": {
                "text_message": {
                    "type": "string",
                    "description": "Text content to publish"
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["facebook", "instagram"]},
                    "description": "List of platforms to publish to",
                    "default": ["facebook"]
                }
            },
            "required": ["text_message"],
            "category": "social_media"
        },
        {
            "name": "meta_publish_image",
            "description": "Publish image content to Facebook and Instagram with optional caption.",
            "function": meta_publish_image,
            "parameters": {
                "image_url": {
                    "type": "string",
                    "description": "URL of image to publish (must be publicly accessible)"
                },
                "caption": {
                    "type": "string",
                    "description": "Optional caption for the image",
                    "default": ""
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["facebook", "instagram"]},
                    "description": "List of platforms to publish to",
                    "default": ["facebook", "instagram"]
                }
            },
            "required": ["image_url"],
            "category": "social_media"
        },
        {
            "name": "meta_publish_text_and_image",
            "description": "Publish text with image to Facebook and Instagram.",
            "function": meta_publish_text_and_image,
            "parameters": {
                "text_message": {
                    "type": "string",
                    "description": "Text content to publish"
                },
                "image_url": {
                    "type": "string",
                    "description": "URL of image to publish (must be publicly accessible)"
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["facebook", "instagram"]},
                    "description": "List of platforms to publish to",
                    "default": ["facebook", "instagram"]
                }
            },
            "required": ["text_message", "image_url"],
            "category": "social_media"
        },
        {
            "name": "meta_get_account_info",
            "description": "Get information about configured Meta accounts (Facebook page and Instagram account).",
            "function": meta_get_account_info,
            "parameters": {},
            "required": [],
            "category": "social_media"
        }
    ]

# # Example usage and testing
# if __name__ == "__main__":
#     # Test account info
#     print("🔍 Testing Meta account info...")
#     info = meta_get_account_info()
#     print(f"Result: {info}")
    
#     # Test text publishing
#     print("\n📝 Testing text publishing...")
#     text_result = meta_publish_text("Hello from the Meta Publisher Tool! 🤖", ["facebook"])
#     print(f"Result: {text_result}")
