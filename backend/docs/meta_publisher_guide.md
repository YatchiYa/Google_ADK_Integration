# Meta Publisher Tools Guide

This guide explains how to use the Meta Publisher Tools integrated into the Google ADK system for publishing content to Facebook and Instagram.

## Overview

The Meta Publisher Tools provide a comprehensive solution for publishing content to your Facebook page and Instagram business account directly from AI agents. The tools support various content types including text, images, and combined text+image posts.

## Available Tools

### 1. `meta_publish_content` - Universal Publisher
The main publishing tool that supports all content types and platforms.

**Parameters:**
- `content_type`: Type of content ("text", "image", "text_with_image")
- `text_message`: Text content to publish
- `image_url`: URL of image to publish (must be publicly accessible)
- `platforms`: List of platforms ("facebook", "instagram", or both)

**Examples:**
```python
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
```

### 2. `meta_publish_text` - Text Publisher
Simplified function for publishing text content.

**Parameters:**
- `text_message`: Text content to publish
- `platforms`: List of platforms (default: ["facebook"])

**Note:** Instagram requires images for most posts, so this primarily works for Facebook.

**Example:**
```python
result = meta_publish_text(
    "Hello from the AI assistant! 🤖",
    platforms=["facebook"]
)
```

### 3. `meta_publish_image` - Image Publisher
Simplified function for publishing images with optional captions.

**Parameters:**
- `image_url`: URL of image to publish
- `caption`: Optional caption for the image
- `platforms`: List of platforms (default: ["facebook", "instagram"])

**Example:**
```python
result = meta_publish_image(
    image_url="https://example.com/sunset.jpg",
    caption="Beautiful sunset! 🌅",
    platforms=["facebook", "instagram"]
)
```

### 4. `meta_publish_text_and_image` - Combined Publisher
Simplified function for publishing text with images.

**Parameters:**
- `text_message`: Text content to publish
- `image_url`: URL of image to publish
- `platforms`: List of platforms (default: ["facebook", "instagram"])

**Example:**
```python
result = meta_publish_text_and_image(
    text_message="Check out this amazing view! 🌅",
    image_url="https://example.com/sunset.jpg",
    platforms=["facebook", "instagram"]
)
```

### 5. `meta_get_account_info` - Account Information
Get information about configured Meta accounts.

**Parameters:** None

**Example:**
```python
info = meta_get_account_info()
print(f"Facebook Page: {info['facebook']['name']}")
print(f"Instagram: @{info['instagram']['username']}")
```

## Configuration

The tools are pre-configured with your specific account IDs:

- **Facebook Page ID:** `861883367002548`
- **Instagram Account ID:** `17841460715803093`

Access tokens are configured in the `meta_publisher_tool.py` file.

## Response Format

All publishing functions return a standardized response:

```python
{
    "success": True/False,
    "platforms_attempted": ["facebook", "instagram"],
    "results": {
        "facebook": {"id": "post_id"} or {"error": {"message": "error_msg"}},
        "instagram": {"id": "post_id"} or {"error": {"message": "error_msg"}}
    },
    "errors": ["list of error messages"],
    "summary": "Human-readable summary of results"
}
```

## Usage in AI Agents

### Agent Prompt Examples

You can instruct AI agents to use these tools with prompts like:

```
"Post this message to Facebook: 'Hello from AI! 🤖'"
"Share this image on Instagram with caption 'Amazing AI art!': https://example.com/image.jpg"
"Post to both Facebook and Instagram: 'Check this out!' with image: https://example.com/photo.jpg"
```

### Tool Selection Logic

The AI agent will automatically choose the appropriate tool based on the request:

- **Text only → Facebook:** Uses `meta_publish_text`
- **Image only:** Uses `meta_publish_image`
- **Text + Image:** Uses `meta_publish_text_and_image`
- **Complex requests:** Uses `meta_publish_content`

## Platform-Specific Notes

### Facebook
- Supports text-only posts
- Supports images with captions
- Supports link sharing
- No special restrictions for basic posting

### Instagram
- **Requires images** for most posts
- Text-only posts are very limited
- Images must be publicly accessible URLs
- Captions support hashtags and mentions

## Image Requirements

For image posting, ensure:

1. **Public URL:** Image must be accessible via HTTP/HTTPS
2. **Supported formats:** JPG, PNG, GIF, WebP
3. **Size limits:** Follow Meta's guidelines (typically max 8MB)
4. **Aspect ratio:** Instagram prefers 1:1 to 4:5 ratio

## Error Handling

Common errors and solutions:

### Authentication Errors
- **Error:** "Invalid access token"
- **Solution:** Update access tokens in configuration

### Image Errors
- **Error:** "Image not accessible"
- **Solution:** Ensure image URL is publicly accessible

### Platform Restrictions
- **Error:** "Instagram requires images"
- **Solution:** Use image-based content types for Instagram

### Rate Limiting
- **Error:** "Rate limit exceeded"
- **Solution:** Wait before retrying, implement backoff logic

## Testing

Use the test script to verify functionality:

```bash
cd backend
python test_meta_tools.py
```

This will run comprehensive tests for all tools and show results.

## Integration with Generated Images

The Meta Publisher Tools work perfectly with the Gemini image generation tools:

```python
# Generate image with Gemini
image_result = gemini_text_to_image("beautiful sunset landscape")

# Publish to social media
if image_result["success"]:
    publish_result = meta_publish_image(
        image_url=image_result["main_image_url"],
        caption="AI-generated sunset landscape! 🎨🌅",
        platforms=["facebook", "instagram"]
    )
```

## Best Practices

1. **Always check success status** before assuming posts were published
2. **Handle errors gracefully** and provide user feedback
3. **Use appropriate content types** for each platform
4. **Include engaging captions** with emojis and hashtags
5. **Test with sample content** before production use
6. **Monitor rate limits** to avoid API restrictions
7. **Keep access tokens secure** and rotate regularly

## Troubleshooting

### Tool Not Found
If agents can't find the tools, restart the backend to reload the tool registry.

### Import Errors
Ensure all dependencies are installed:
```bash
pip install requests loguru
```

### Configuration Issues
Check that account IDs and access tokens are correctly set in `meta_publisher_tool.py`.

## Support

For issues or questions:
1. Check the error messages in the response
2. Review the logs for detailed debugging information
3. Test with the provided test script
4. Verify account permissions and access tokens

The Meta Publisher Tools provide a powerful way to automate social media posting from your AI agents, enabling seamless content distribution across Facebook and Instagram platforms.
