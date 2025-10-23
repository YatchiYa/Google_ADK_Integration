# Personal Social Media Accounts Setup Guide

This guide will help you set up access to **personal Instagram and Facebook accounts** in addition to your existing business account access.

## 🎯 **What You'll Get**

After setup, you'll be able to access:
- ✅ **Personal Instagram** (@mamba_happy_world) - profile, media, followers
- ✅ **Personal Facebook** - profile, posts, photos (limited)
- ✅ **Business Accounts** - Facebook pages, Instagram business (already working)

## 📋 **Prerequisites**

- Facebook Developer Account
- Access to your personal Instagram account (@mamba_happy_world)
- Basic understanding of OAuth flows

## 🔧 **Step 1: Instagram Basic Display API Setup**

### **1.1 Create Instagram Basic Display App**

1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Click **"Create App"**
3. Select **"Consumer"** → **"Next"**
4. Choose **"Instagram Basic Display"**
5. Fill in app details:
   - **App Name**: "Personal Instagram Access" (or any name)
   - **Contact Email**: Your email
   - Click **"Create App"**

### **1.2 Configure Instagram Basic Display**

1. In your app dashboard, go to **"Instagram Basic Display"** → **"Basic Display"**
2. Click **"Create New App"**
3. Set up the following:
   - **Display Name**: Your app name
   - **Valid OAuth Redirect URIs**: `https://localhost:8000/callback` (or your domain)
   - **Deauthorize Callback URL**: `https://localhost:8000/deauth`
   - **Data Deletion Request URL**: `https://localhost:8000/delete`

### **1.3 Add Instagram Tester**

1. Go to **"Roles"** → **"Roles"**
2. Click **"Add Instagram Testers"**
3. Enter your Instagram username: `mamba_happy_world`
4. Click **"Submit"**
5. **Important**: Go to your Instagram app and accept the tester invitation

### **1.4 Get App Credentials**

1. Go to **"Instagram Basic Display"** → **"Basic Display"**
2. Note down:
   - **Instagram App ID**
   - **Instagram App Secret**

## 🔧 **Step 2: Generate Instagram Access Token**

### **2.1 Use the Helper Functions**

Add this code to test your setup:

```python
# Your app credentials
INSTAGRAM_APP_ID = "your_instagram_app_id_here"
INSTAGRAM_APP_SECRET = "your_instagram_app_secret_here"
REDIRECT_URI = "https://localhost:8000/callback"

# Generate authorization URL
auth_url = generate_instagram_basic_auth_url(INSTAGRAM_APP_ID, REDIRECT_URI)
print(f"Visit this URL: {auth_url}")
```

### **2.2 Authorization Flow**

1. **Run the code above** to get the authorization URL
2. **Visit the URL** in your browser
3. **Log in** with your personal Instagram account (@mamba_happy_world)
4. **Authorize** the app
5. **Copy the code** from the redirect URL (after `?code=`)

### **2.3 Exchange Code for Token**

```python
# Replace 'AUTHORIZATION_CODE' with the code from step 2.2
code = "AUTHORIZATION_CODE_FROM_REDIRECT"

# Exchange code for access token
token_data = exchange_instagram_code_for_token(
    INSTAGRAM_APP_ID, 
    INSTAGRAM_APP_SECRET, 
    REDIRECT_URI, 
    code
)

print(f"Access Token: {token_data['access_token']}")

# Get long-lived token (60 days)
long_token = get_long_lived_instagram_token(
    token_data['access_token'], 
    INSTAGRAM_APP_SECRET
)

print(f"Long-lived Token: {long_token['access_token']}")
```

### **2.4 Update Configuration**

In `main.py`, update the token:

```python
# Personal Account Access Tokens
INSTAGRAM_BASIC_ACCESS_TOKEN = "your_long_lived_token_here"
```

## 🔧 **Step 3: Facebook Personal Account Setup**

### **3.1 Request Additional Permissions**

For personal Facebook access, you need additional permissions:

1. Go to your **Facebook App Dashboard**
2. Go to **"App Review"** → **"Permissions and Features"**
3. Request these permissions:
   - `user_posts` - Read user's posts
   - `user_photos` - Read user's photos
   - `user_videos` - Read user's videos

**Note**: These require app review and are rarely approved for personal use.

### **3.2 Alternative: Use Current Token**

Your current token might already have personal profile access. The library will automatically try to use it for personal Facebook data.

## 🧪 **Step 4: Test Your Setup**

Run the updated demo:

```bash
python3 main.py
```

You should now see:

```
📊 BUSINESS ACCOUNTS SUMMARY:
   Facebook Pages: 2
   Instagram Business: 1

📊 PERSONAL ACCOUNTS SUMMARY:
   Personal Instagram: @mamba_happy_world
   Instagram Media: 150
   Personal Facebook: Joseph Kïñg
```

## 🎯 **Step 5: Use Personal Account Functions**

### **Personal Instagram**
```python
# Get personal Instagram profile
profile = get_personal_instagram_profile()
print(f"Username: @{profile['username']}")
print(f"Followers: {profile['followers_count']}")

# Get personal Instagram media
media = get_personal_instagram_media(limit=10)
for item in media['data']:
    print(f"Media: {item['media_type']} - {item.get('caption', 'No caption')}")
```

### **Personal Facebook**
```python
# Get personal Facebook profile
profile = get_personal_facebook_profile()
print(f"Name: {profile['name']}")

# Get personal Facebook posts (if permissions available)
posts = get_personal_facebook_posts(limit=5)
for post in posts.get('data', []):
    print(f"Post: {post.get('message', 'No message')}")
```

### **Universal Access**
```python
# Get all accounts (business + personal)
all_accounts = get_all_personal_social_accounts()
print(f"Personal Instagram: @{all_accounts['personal_instagram']['username']}")
print(f"Personal Facebook: {all_accounts['personal_facebook']['name']}")
```

## ⚠️ **Important Notes**

### **Instagram Basic Display Limitations**
- **Read-only access** - Cannot post to personal Instagram
- **25 media items max** per request
- **Limited to basic profile data**
- **Requires user authorization** every 60 days

### **Facebook Personal Account Limitations**
- **Personal timeline posting** is heavily restricted
- **Most permissions require app review**
- **Limited to profile data** with standard tokens
- **Cannot post to personal timeline** without special permissions

### **Token Management**
- **Instagram tokens expire** after 60 days
- **Refresh tokens** using the provided functions
- **Store tokens securely** in production
- **Never commit tokens** to version control

## 🔗 **Helpful Resources**

- [Instagram Basic Display API Docs](https://developers.facebook.com/docs/instagram-basic-display-api)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [Facebook App Dashboard](https://developers.facebook.com/apps/)
- [Instagram Basic Display API Testing](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started)

## 🆘 **Troubleshooting**

### **"Invalid OAuth access token"**
- Check if your Instagram app is in Development mode
- Ensure you've added yourself as an Instagram Tester
- Verify the access token hasn't expired

### **"User not authorized"**
- Make sure you accepted the Instagram tester invitation
- Check if your Instagram account is connected to a Facebook account

### **"Permission denied"**
- Some Facebook permissions require app review
- Personal timeline posting is restricted for most apps
- Use business accounts for posting capabilities

## ✅ **Success Checklist**

- [ ] Instagram Basic Display app created
- [ ] Instagram tester added and accepted
- [ ] Authorization flow completed
- [ ] Long-lived token generated
- [ ] Token added to configuration
- [ ] Demo shows personal Instagram data
- [ ] Personal Facebook profile accessible

Once you complete this setup, you'll have access to both business and personal social media accounts through your Python library!
