# Facebook Authentication Setup Guide

## Step 1: Create Frontend Environment File

Create the file `/home/yarab/Bureau/perso/jinxai/Google_ADK_Integration/frontend/.env.local` with:

```bash
NEXT_PUBLIC_FACEBOOK_APP_ID=450270912741955
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 2: Facebook App Configuration

1. **Go to Facebook Developers Console**: https://developers.facebook.com/apps/450270912741955/

2. **Configure Basic Settings**:
   - App ID: `450270912741955`
   - App Secret: (keep this secure)
   - App Domains: Add your domain (e.g., `localhost`, `yourdomain.com`)

3. **Add Facebook Login Product**:
   - Go to "Add Product" → "Facebook Login"
   - Configure OAuth Redirect URIs:
     ```
     http://localhost:3000/
     https://yourdomain.com/
     ```

4. **Configure App Review & Permissions**:
   - Go to "App Review" → "Permissions and Features"
   - Request these permissions (some require app review):

   **Basic Permissions (usually auto-approved):**
   - `public_profile`
   - `email`
   - `pages_show_list`

   **Advanced Permissions (require review):**
   - `user_likes`
   - `user_events`
   - `user_photos`
   - `user_videos`
   - `user_posts`
   - `user_messenger_contact`
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_manage_metadata`
   - `pages_read_user_content`
   - `pages_manage_engagement`
   - `pages_manage_instant_articles`
   - `page_events`
   - `read_insights`
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_branded_content_brand`
   - `instagram_branded_content_creator`
   - `instagram_branded_content_ads_brand`
   - `instagram_manage_events`
   - `business_management`
   - `ads_management`
   - `ads_read`
   - `manage_app_solution`

5. **App Modes**:
   - **Development Mode**: Use for testing with test users
   - **Live Mode**: Requires app review for advanced permissions

## Step 3: Test User Setup (for Development)

If your app is in Development Mode:

1. Go to "Roles" → "Test Users"
2. Create test users or add real users as "Testers"
3. Test users can use all permissions without app review

## Step 4: Page Requirements

To see pages in the connection panel:

1. **User must be Page Admin/Editor**: The Facebook user must have admin or editor role on pages
2. **Page must be published**: Unpublished pages may not appear
3. **Business verification**: Some permissions require business verification

## Step 5: Instagram Business Account

For Instagram publishing:

1. **Convert to Business Account**: Instagram account must be a Business account
2. **Connect to Facebook Page**: Instagram Business account must be connected to a Facebook Page
3. **Page Admin Access**: User must be admin of the connected Facebook Page

## Step 6: Debugging Steps

### Check Browser Console

Open browser developer tools and look for:
```javascript
🔧 Facebook App ID: 450270912741955
✅ Facebook SDK initialized
🔍 Fetching user pages...
📄 Raw pages response: {...}
📄 Facebook pages loaded: X pages
```

### Common Issues

1. **"No Pages Found"**:
   - User is not admin/editor of any pages
   - Pages are unpublished
   - Missing `pages_show_list` permission

2. **"Invalid App ID"**:
   - Check App ID in environment file
   - Verify App ID in Facebook Developer Console
   - Check domain configuration

3. **"Permission Denied"**:
   - User declined permissions
   - App doesn't have required permissions approved
   - Need to request permissions again

### Test Commands

In browser console:
```javascript
// Check if Facebook SDK is loaded
console.log(window.FB);

// Check current login status
FB.getLoginStatus(console.log);

// Check user permissions
FB.api('/me/permissions', console.log);

// Check user pages
FB.api('/me/accounts', console.log);
```

## Step 7: Production Deployment

For production:

1. **Submit App for Review**: Submit your app with required permissions
2. **Business Verification**: Complete business verification if required
3. **Update Environment**: Set production App ID and domains
4. **SSL Certificate**: Ensure HTTPS for OAuth redirects
5. **Privacy Policy**: Add privacy policy URL to app settings

## Troubleshooting Checklist

- [ ] Environment file created with correct App ID
- [ ] Facebook app configured with correct domains
- [ ] OAuth redirect URIs added
- [ ] User has admin access to Facebook pages
- [ ] Pages are published and active
- [ ] Required permissions requested/approved
- [ ] Instagram accounts are Business accounts (if using Instagram)
- [ ] Instagram accounts connected to Facebook pages

## Support

If you continue having issues:

1. Check Facebook Developer Console for error messages
2. Review app review status for permissions
3. Test with different Facebook accounts
4. Verify page admin roles
5. Check browser console for detailed error logs
