# Facebook Authentication System Guide

This guide explains the complete Facebook authentication system integrated into the Google ADK platform for automatic Meta publishing.

## Overview

The Facebook authentication system provides seamless integration between your frontend application and Meta's APIs, allowing AI agents to automatically publish content to Facebook pages and Instagram accounts with proper user authorization.

## System Architecture

### Frontend Components
1. **FacebookService** (`/frontend/src/services/facebook.service.ts`)
2. **FacebookLoginButton** (`/frontend/src/components/FacebookLoginButton.tsx`)
3. **FacebookConnectionPanel** (`/frontend/src/components/FacebookConnectionPanel.tsx`)

### Backend Components
1. **Meta Publisher Tools** (`/backend/tools/meta_publisher_tool.py`)
2. **Meta Auth Router** (`/backend/routers/meta_auth.py`)
3. **Tool Manager Integration** (`/backend/managers/tool_manager.py`)

## Facebook App Configuration

### Required App Setup
1. **Create Facebook App**:
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create new app → Business → App name
   - Add Facebook Login product
   - Add Instagram Basic Display (for personal accounts)

2. **Configure App Settings**:
   ```javascript
   App ID: YOUR_FACEBOOK_APP_ID
   App Secret: YOUR_FACEBOOK_APP_SECRET
   Valid OAuth Redirect URIs: https://yourdomain.com/
   ```

3. **Required Permissions**:
   ```javascript
   // Business permissions (for pages/Instagram business)
   pages_manage_posts
   pages_read_engagement
   pages_show_list
   instagram_basic
   instagram_content_publish
   business_management
   pages_manage_metadata
   pages_read_user_content
   
   // Personal permissions (optional)
   user_posts
   user_photos
   ```

### Environment Variables
```bash
# Frontend (.env.local)
NEXT_PUBLIC_FACEBOOK_APP_ID=your_app_id_here
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (.env)
# No additional Facebook env vars needed - tokens come from frontend
```

## Authentication Flow

### 1. Frontend Authentication
```typescript
// Initialize Facebook SDK
const FacebookService = new FacebookServiceClass();

// User clicks login button
const authState = await FacebookService.login();

// Get user's pages and Instagram accounts
const pages = authState.pages;
const instagramAccounts = authState.instagram_accounts;
```

### 2. Token Management
```typescript
// Get tokens for publishing
const tokens = FacebookService.getMetaPublisherTokens();
// Returns:
// {
//   userAccessToken: "user_token",
//   pageAccessToken: "page_token", 
//   instagramAccountId: "ig_account_id",
//   pageId: "page_id"
// }
```

### 3. Backend Synchronization
```typescript
// Send tokens to backend
const response = await fetch('/api/v1/meta/tokens', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': userApiKey
  },
  body: JSON.stringify(tokens)
});
```

### 4. AI Agent Publishing
```python
# Agent can now use Meta publisher tools
result = meta_publish_content(
    content_type="text_with_image",
    text_message="Hello from AI! 🤖",
    image_url="https://example.com/image.jpg",
    platforms=["facebook", "instagram"]
)
```

## Frontend Integration

### Basic Usage
```tsx
import FacebookLoginButton from '@/components/FacebookLoginButton';

function MyComponent() {
  const handleAuthChange = (authState) => {
    console.log('Facebook auth changed:', authState);
    if (authState.isConnected) {
      // User is connected, sync tokens
      syncTokensWithBackend(authState);
    }
  };

  return (
    <FacebookLoginButton
      onAuthChange={handleAuthChange}
      onError={(error) => console.error(error)}
      size="md"
      variant="primary"
      showStatus={true}
    />
  );
}
```

### Chat Integration
```tsx
import FacebookConnectionPanel from '@/components/FacebookConnectionPanel';

function ChatPage({ agentId, sessionId }) {
  return (
    <div className="sidebar">
      <FacebookConnectionPanel
        agentId={agentId}
        sessionId={sessionId}
        onConnectionChange={(connected) => {
          console.log('Facebook connected:', connected);
        }}
      />
    </div>
  );
}
```

## Backend API Endpoints

### Update Tokens
```http
POST /api/v1/meta/tokens
Content-Type: application/json
X-API-Key: user_api_key

{
  "user_access_token": "user_token",
  "page_access_token": "page_token",
  "page_id": "123456789",
  "instagram_account_id": "ig_123456"
}
```

### Get Token Status
```http
GET /api/v1/meta/tokens/status
X-API-Key: user_api_key

Response:
{
  "success": true,
  "has_tokens": true,
  "page_id": "123456789",
  "instagram_account_id": "ig_123456"
}
```

### Test Connection
```http
POST /api/v1/meta/test-connection
X-API-Key: user_api_key

Response:
{
  "success": true,
  "facebook_status": "active",
  "instagram_status": "active",
  "errors": []
}
```

## AI Agent Tools

### Available Tools
1. **meta_publish_content** - Universal publisher
2. **meta_publish_text** - Text-only publishing
3. **meta_publish_image** - Image publishing
4. **meta_publish_text_and_image** - Combined publishing
5. **meta_get_account_info** - Account information
6. **update_meta_tokens** - Token management

### Example Agent Usage
```python
# Agent prompt examples:
"Post this to Facebook: 'Hello from AI! 🤖'"
"Share this image on Instagram with caption 'AI generated art!'"
"Post to both Facebook and Instagram: 'Check this out!' with image: https://..."
```

## Token Security

### Frontend Security
- Tokens stored in localStorage with expiry checking
- Automatic token refresh when needed
- Secure transmission to backend via HTTPS
- User can logout/disconnect anytime

### Backend Security
- Tokens stored in memory (not persistent)
- 24-hour token expiry for security
- API key authentication required
- No tokens logged in production

### Best Practices
1. **Token Rotation**: Refresh tokens regularly
2. **Minimal Permissions**: Only request needed permissions
3. **Secure Storage**: Use secure storage in production
4. **Error Handling**: Graceful handling of expired tokens
5. **User Control**: Allow users to disconnect anytime

## Troubleshooting

### Common Issues

#### 1. "App Not Approved" Error
- **Cause**: App needs Facebook review for certain permissions
- **Solution**: Submit app for review or use test users

#### 2. "Invalid OAuth Redirect URI"
- **Cause**: Redirect URI not configured in Facebook app
- **Solution**: Add your domain to Valid OAuth Redirect URIs

#### 3. "Token Expired" Error
- **Cause**: Access token has expired
- **Solution**: User needs to re-authenticate

#### 4. "Permission Denied" Error
- **Cause**: User didn't grant required permissions
- **Solution**: Request permissions again with proper scope

#### 5. "Page Not Found" Error
- **Cause**: User doesn't have access to the page
- **Solution**: Ensure user is admin/editor of the page

### Debug Mode
```typescript
// Enable debug logging
localStorage.setItem('facebook_debug', 'true');

// Check token status
const tokens = FacebookService.getMetaPublisherTokens();
console.log('Current tokens:', tokens);

// Test API connection
const status = await fetch('/api/v1/meta/tokens/status');
console.log('Backend status:', await status.json());
```

## Production Deployment

### Frontend Configuration
```bash
# Production environment variables
NEXT_PUBLIC_FACEBOOK_APP_ID=your_production_app_id
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Backend Configuration
```python
# Update CORS settings for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSL Requirements
- Facebook requires HTTPS for OAuth redirects
- Ensure your domain has valid SSL certificate
- Update Facebook app settings with HTTPS URLs

## Monitoring and Analytics

### Key Metrics to Track
1. **Authentication Success Rate**
2. **Token Refresh Frequency**
3. **Publishing Success Rate**
4. **Error Rates by Type**
5. **User Connection Duration**

### Logging
```python
# Backend logging
logger.info(f"Facebook auth successful for user {user_id}")
logger.error(f"Token sync failed: {error}")

# Frontend logging
console.log('Facebook SDK initialized');
console.error('Authentication failed:', error);
```

## Support and Maintenance

### Regular Tasks
1. **Monitor token expiry rates**
2. **Update Facebook SDK versions**
3. **Review and renew app permissions**
4. **Check for API deprecations**
5. **Update documentation**

### Facebook API Changes
- Subscribe to Facebook Developer updates
- Test with new API versions
- Update SDK and permissions as needed
- Maintain backward compatibility

This comprehensive authentication system provides a seamless, secure way for users to connect their Facebook and Instagram accounts, enabling AI agents to publish content automatically with proper authorization.
