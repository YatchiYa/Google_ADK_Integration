# HTTPS Setup Guide for Facebook Authentication

## 🚨 **Problem**
Facebook requires HTTPS for all SDK calls since 2018. Your development server is running on HTTP (`http://localhost:3000`), causing Facebook API calls to fail.

## 🔧 **Solution Options**

### **Option 1: Enable HTTPS in Development (Recommended)**

#### Step 1: Generate SSL Certificates
```bash
cd /home/yarab/Bureau/perso/jinxai/Google_ADK_Integration/frontend

# Make the script executable
chmod +x generate-ssl.sh

# Generate SSL certificates
npm run generate-ssl
```

#### Step 2: Start HTTPS Development Server
```bash
# Start with HTTPS
npm run dev:https
```

#### Step 3: Access Your App
- Open: `https://localhost:3000`
- **Important**: Your browser will show a security warning
- Click **"Advanced"** → **"Proceed to localhost (unsafe)"**

#### Step 4: Update Facebook App Settings
In Facebook Developer Console (`https://developers.facebook.com/apps/450270912741955/`):

1. **Go to Settings → Basic**
2. **Update App Domains**: Add `localhost`
3. **Go to Facebook Login → Settings**
4. **Update Valid OAuth Redirect URIs**:
   ```
   https://localhost:3000/
   https://localhost:3000/chat
   ```

### **Option 2: Use ngrok for Public HTTPS (Alternative)**

#### Step 1: Install ngrok
```bash
# Install ngrok (if not installed)
npm install -g ngrok
```

#### Step 2: Start Your Development Server
```bash
# In one terminal
npm run dev
```

#### Step 3: Create HTTPS Tunnel
```bash
# In another terminal
ngrok http 3000
```

#### Step 4: Use ngrok HTTPS URL
- ngrok will provide an HTTPS URL like: `https://abc123.ngrok.io`
- Use this URL instead of localhost
- Update Facebook App settings with this URL

### **Option 3: Disable Facebook Features for Development**

If you want to test other features without Facebook:

#### Step 1: Create Development Flag
Add to `/frontend/.env.local`:
```bash
NEXT_PUBLIC_FACEBOOK_APP_ID=450270912741955
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DISABLE_FACEBOOK=true
```

#### Step 2: Update Facebook Service
The service will automatically detect HTTP and show warnings instead of errors.

## 🔧 **Files Created/Modified**

### ✅ **New Files**:
- `/frontend/https-server.js` - HTTPS development server
- `/frontend/generate-ssl.sh` - SSL certificate generator
- `/frontend/HTTPS_SETUP_GUIDE.md` - This guide

### ✅ **Modified Files**:
- `/frontend/package.json` - Added HTTPS scripts
- `/frontend/src/services/facebook.service.ts` - Added HTTPS detection

## 🚀 **Quick Start Commands**

```bash
# Navigate to frontend
cd /home/yarab/Bureau/perso/jinxai/Google_ADK_Integration/frontend

# Generate SSL certificates
chmod +x generate-ssl.sh && npm run generate-ssl

# Start HTTPS development server
npm run dev:https

# Open in browser (accept security warning)
# https://localhost:3000
```

## 🔧 **Facebook Developer Console Setup**

### **Required Settings**:

1. **App Domains**: `localhost`
2. **Valid OAuth Redirect URIs**:
   ```
   https://localhost:3000/
   https://localhost:3000/chat/
   ```
3. **App Review**: Request permissions for production use

### **Required Permissions**:
```
public_profile, email, pages_show_list, pages_manage_posts, 
pages_read_engagement, pages_manage_metadata, pages_read_user_content, 
pages_manage_engagement, instagram_basic, instagram_content_publish, 
business_management
```

## 🧪 **Testing Steps**

1. **Start HTTPS server**: `npm run dev:https`
2. **Open**: `https://localhost:3000`
3. **Accept security warning**
4. **Go to chat page**
5. **Click "Connect Facebook"** in sidebar
6. **Complete OAuth flow**
7. **Verify pages are loaded**

## ⚠️ **Common Issues**

### **"NET::ERR_CERT_AUTHORITY_INVALID"**
- **Solution**: Click "Advanced" → "Proceed to localhost (unsafe)"
- **Cause**: Self-signed certificates trigger browser warnings

### **"App Not Setup: This app is still in development mode"**
- **Solution**: Add test users in Facebook Developer Console
- **Or**: Submit app for review for public use

### **"Invalid Redirect URI"**
- **Solution**: Ensure redirect URIs in Facebook app match your HTTPS URL
- **Check**: `https://localhost:3000/` (with trailing slash)

### **Still Getting HTTP Errors**
- **Check**: Browser is using `https://` not `http://`
- **Clear**: Browser cache and cookies
- **Verify**: Facebook app settings are saved

## 🔄 **Switching Between HTTP/HTTPS**

### **For Facebook Development**:
```bash
npm run dev:https  # Use HTTPS
```

### **For Other Development**:
```bash
npm run dev        # Use HTTP
```

## 📝 **Next Steps After HTTPS Setup**

1. ✅ **Test Facebook Connection**
2. ✅ **Verify Page Discovery**  
3. ✅ **Test Meta Publishing Tools**
4. ✅ **Test Document RAG Tool**

Your Facebook authentication should now work properly with HTTPS! 🎉
