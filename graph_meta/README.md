# Facebook Graph API Library

A comprehensive, AI-agent-friendly Python library for Facebook Graph API interactions.

## 🎯 **Features**

### **User Information Functions**
- `get_current_user_profile()` - Get authenticated user's profile
- `get_user_facebook_pages()` - Get all accessible Facebook pages
- `get_page_connected_instagram_account()` - Get Instagram account linked to a page
- `get_all_user_social_accounts()` - Get comprehensive social media overview

### **Facebook Page Posting Functions**
- `post_text_to_facebook_page()` - Post text-only messages
- `post_image_to_facebook_page()` - Post images from URLs
- `upload_local_image_to_facebook_page()` - Upload local image files
- `post_link_to_facebook_page()` - Share links with messages
- `post_text_with_image_to_facebook_page()` - Combined text and image posts

### **Instagram Posting Functions**
- `post_text_to_instagram_account()` - Post text (limited support)
- `post_image_to_instagram_account()` - Post images with captions
- `post_text_with_image_to_instagram_account()` - Combined posts
- `publish_instagram_media()` - Publish created media containers

### **AI Agent Utility Functions**
- `find_facebook_page_by_name()` - Find page by name (case-insensitive)
- `find_instagram_account_by_username()` - Find Instagram by username
- `get_page_access_token_by_page_name()` - Get access token by page name
- `post_to_social_media_by_name()` - **Universal posting function for AI agents**

## 🤖 **Perfect for AI Agents**

### **Universal Posting Interface**
```python
# Post to Facebook
result = post_to_social_media_by_name(
    platform="facebook",
    account_name="My Business Page",
    content_type="text",
    text_message="Hello World!"
)

# Post to Instagram
result = post_to_social_media_by_name(
    platform="instagram", 
    account_name="mybusiness",
    content_type="image",
    image_url="https://example.com/image.jpg",
    caption="Amazing photo!"
)
```

### **Content Types Supported**
- `"text"` - Text-only posts
- `"image"` - Image with optional caption
- `"text_with_image"` - Text message with image
- `"link"` - Link sharing (Facebook only)

## 📚 **Function Documentation**

Every function includes:
- **Clear parameter descriptions**
- **Return value documentation** 
- **Usage examples**
- **Type hints**
- **Error handling**

## 🚀 **Quick Start**

1. **Set your access token** in the `ACCESS_TOKEN` variable
2. **Get user information:**
   ```python
   accounts = get_all_user_social_accounts()
   print(f"Facebook Pages: {accounts['total_pages']}")
   print(f"Instagram Accounts: {accounts['total_instagram_accounts']}")
   ```

3. **Post content:**
   ```python
   # Direct function call
   result = post_text_to_facebook_page(page_id, page_token, "Hello!")
   
   # AI-friendly universal function
   result = post_to_social_media_by_name("facebook", "Page Name", "text", text_message="Hello!")
   ```

## 🛠 **Demo Functions**

- `demo_user_information()` - Shows user profile and social accounts
- `demo_posting_functions()` - Demonstrates posting capabilities  
- `demo_all_features()` - Comprehensive feature demo

## 📋 **Requirements**

```python
import requests
import json
from typing import Dict, List, Optional, Union
```

## 🔧 **Configuration**

Update these constants at the top of the file:
- `ACCESS_TOKEN` - Your Facebook Graph API access token
- `GRAPH_API_VERSION` - API version (default: "v20.0")
- `BASE_URL` - Graph API base URL

## ✅ **Error Handling**

All functions return dictionaries with either:
- **Success**: `{'id': 'post_id', ...}`
- **Error**: `{'error': {'message': 'Error description'}}`

## 🎯 **AI Agent Benefits**

1. **Simple Interface**: One universal function for all posting needs
2. **Clear Naming**: Function names clearly indicate their purpose
3. **Comprehensive Docs**: Every function has examples and parameter descriptions
4. **Error Handling**: Consistent error response format
5. **Type Safety**: Full type hints for better AI understanding
6. **Account Discovery**: Find accounts by name instead of remembering IDs

This library is specifically designed to be easily understood and used by AI agents for social media automation tasks.
