import requests
import json
import time
from typing import Dict, List, Optional, Union

# Configuration
ACCESS_TOKEN = "EAAGZAhN3OgkMBPzCrQ3EkneaZBlWdG0Q9oCeUbOkHK2WtpHLllkFCMJ1CEoytII2wgJSScJNsNLlZBp4TN6Al841VGzkeTA7DBeWTXnsyeBVZCFW30swM16XZAhvs57WfoT6mwjwfUOddMGBX5KP6eXZBgkv9MgmFxBzSuJQSGHywIL81dThyjOgAx3iJn3QjGJucxZBj6e9lNZBflul81L01NRZBSI6lMu4ZCh6i5xagPsdVffSILfpbKQleo8NYjRJ1BtgafM9yEruKO7kqj"
GRAPH_API_VERSION = "v24.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Personal Account Access Tokens (you'll need to get these separately)
INSTAGRAM_BASIC_ACCESS_TOKEN = ""  # For personal Instagram access
FACEBOOK_USER_ACCESS_TOKEN = ""    # For personal Facebook access (if different from main token)

# ============================================================================
# USER INFORMATION FUNCTIONS
# ============================================================================

def get_current_user_profile() -> Dict:
    """
    Get the current authenticated user's profile information.
    
    Returns:
        Dict containing user ID, name, email, first_name, last_name
        
    Example:
        user_info = get_current_user_profile()
        print(f"User: {user_info['name']}")
    """
    url = f"{BASE_URL}/me"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,email,first_name,last_name'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_user_facebook_pages() -> Dict:
    """
    Get all Facebook pages that the current user has access to manage.
    
    Returns:
        Dict containing list of pages with their details and access tokens
        
    Example:
        pages = get_user_facebook_pages()
        for page in pages['data']:
            print(f"Page: {page['name']} (ID: {page['id']})")
    """
    url = f"{BASE_URL}/me/accounts"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,category,access_token,tasks,instagram_business_account'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_user_business_portfolios() -> Dict:
    """
    Get all business portfolios that the user has access to.
    Business portfolios contain pages managed through Meta Business Suite.
    
    Returns:
        Dict containing list of business portfolios
        
    Example:
        portfolios = get_user_business_portfolios()
        for portfolio in portfolios.get('data', []):
            print(f"Portfolio: {portfolio['name']} (ID: {portfolio['id']})")
    """
    url = f"{BASE_URL}/me/business_users"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'business{id,name,verification_status}'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_user_businesses() -> Dict:
    """
    Alternative method to get businesses using /me/businesses endpoint.
    
    Returns:
        Dict containing list of businesses
    """
    url = f"{BASE_URL}/me/businesses"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,verification_status,profile_picture_uri'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_user_managed_pages() -> Dict:
    """
    Get pages where user has specific management roles.
    This might catch pages not returned by /me/accounts.
    
    Returns:
        Dict containing managed pages
    """
    url = f"{BASE_URL}/me/accounts"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,category,access_token,tasks,instagram_business_account,perms',
        'limit': 100  # Increase limit to catch more pages
    }
    
    response = requests.get(url, params=params)
    return response.json()

def search_pages_by_name(page_name: str) -> Dict:
    """
    Search for pages by name. This can help find pages that might not appear in /me/accounts.
    
    Args:
        page_name: Name of the page to search for
        
    Returns:
        Dict containing search results
    """
    url = f"{BASE_URL}/search"
    params = {
        'access_token': ACCESS_TOKEN,
        'q': page_name,
        'type': 'page',
        'fields': 'id,name,category,instagram_business_account'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_specific_page_info(page_id: str) -> Dict:
    """
    Get information about a specific page by ID.
    Useful when you know the page ID but it's not appearing in other endpoints.
    
    Args:
        page_id: The Facebook page ID
        
    Returns:
        Dict containing page information
    """
    url = f"{BASE_URL}/{page_id}"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,category,instagram_business_account,tasks,access_token'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_business_portfolio_pages(business_id: str) -> Dict:
    """
    Get all pages owned by a specific business portfolio.
    
    Args:
        business_id: The business portfolio ID
        
    Returns:
        Dict containing pages owned by the business portfolio
        
    Example:
        pages = get_business_portfolio_pages("business_123")
        for page in pages.get('data', []):
            print(f"Business Page: {page['name']}")
    """
    url = f"{BASE_URL}/{business_id}/owned_pages"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,category,instagram_business_account,tasks'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_business_portfolio_instagram_accounts(business_id: str) -> Dict:
    """
    Get all Instagram accounts owned by a specific business portfolio.
    
    Args:
        business_id: The business portfolio ID
        
    Returns:
        Dict containing Instagram accounts owned by the business portfolio
        
    Example:
        ig_accounts = get_business_portfolio_instagram_accounts("business_123")
        for ig in ig_accounts.get('data', []):
            print(f"Business Instagram: @{ig['username']}")
    """
    url = f"{BASE_URL}/{business_id}/owned_instagram_accounts"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name,username,profile_picture_url,followers_count,media_count'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_page_access_token(page_id: str) -> Dict:
    """
    Get access token for a specific page using the user's access token.
    This is needed for pages managed through business portfolios.
    
    Args:
        page_id: The Facebook page ID
        
    Returns:
        Dict containing page access token or error
        
    Example:
        token_data = get_page_access_token("123456789")
        if 'access_token' in token_data:
            print(f"Page token: {token_data['access_token']}")
    """
    url = f"{BASE_URL}/{page_id}"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'access_token,name,id'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_instagram_account_details(instagram_account_id: str, page_access_token: str) -> Dict:
    """
    Get detailed information about a specific Instagram business account.
    
    Args:
        instagram_account_id: Instagram business account ID
        page_access_token: Access token from connected Facebook page
        
    Returns:
        Dict containing Instagram account details
        
    Example:
        details = get_instagram_account_details("17841460715803093", "page_token")
        print(f"Instagram: @{details.get('username', 'N/A')}")
    """
    url = f"{BASE_URL}/{instagram_account_id}"
    params = {
        'access_token': page_access_token,
        'fields': 'id,name,username,profile_picture_url,followers_count,media_count,biography'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_page_connected_instagram_account(page_id: str, page_access_token: str) -> Dict:
    """
    Get Instagram business account connected to a specific Facebook page.
    
    Args:
        page_id: Facebook page ID
        page_access_token: Access token for the specific page
        
    Returns:
        Dict containing Instagram account details if connected
        
    Example:
        ig_account = get_page_connected_instagram_account("123456", "page_token")
        if 'instagram_business_account' in ig_account:
            print(f"Instagram: @{ig_account['instagram_business_account']['username']}")
    """
    url = f"{BASE_URL}/{page_id}"
    params = {
        'access_token': page_access_token,
        'fields': 'instagram_business_account{id,name,username,profile_picture_url,followers_count}'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_all_user_social_accounts() -> Dict:
    """
    Get comprehensive list of all Facebook pages and connected Instagram accounts.
    Includes both personal pages and business portfolio pages.
    
    Returns:
        Dict with structured information about all accessible social accounts
        
    Example:
        accounts = get_all_user_social_accounts()
        print(f"Found {len(accounts['facebook_pages'])} Facebook pages")
        print(f"Found {len(accounts['instagram_accounts'])} Instagram accounts")
    """
    result = {
        'user_profile': {},
        'facebook_pages': [],
        'instagram_accounts': [],
        'business_portfolios': [],
        'business_portfolio_pages': [],
        'business_portfolio_instagram': [],
        'total_pages': 0,
        'total_instagram_accounts': 0,
        'total_business_portfolios': 0
    }
    
    # Get user profile
    result['user_profile'] = get_current_user_profile()
    
    # Get Facebook pages
    pages_response = get_user_facebook_pages()
    if 'data' in pages_response:
        result['facebook_pages'] = pages_response['data']
        result['total_pages'] = len(pages_response['data'])
        
        # Check each page for connected Instagram
        for page in pages_response['data']:
            if 'instagram_business_account' in page and page['instagram_business_account']:
                # Instagram account data is already in the page response
                ig_account_id = page['instagram_business_account']['id']
                
                try:
                    # Get detailed Instagram info using the account ID
                    ig_details = get_page_connected_instagram_account(page['id'], page['access_token'])
                    if 'instagram_business_account' in ig_details:
                        ig_account = ig_details['instagram_business_account']
                    else:
                        # Fallback: use the basic data from page response and get more details
                        ig_account = page['instagram_business_account']
                        # Try to get additional details directly
                        try:
                            ig_url = f"{BASE_URL}/{ig_account_id}"
                            ig_params = {
                                'access_token': page['access_token'],
                                'fields': 'id,name,username,profile_picture_url,followers_count,media_count'
                            }
                            ig_response = requests.get(ig_url, params=ig_params)
                            ig_data = ig_response.json()
                            if 'error' not in ig_data:
                                ig_account.update(ig_data)
                        except Exception as detail_error:
                            print(f"Could not get detailed Instagram info for {page['name']}: {detail_error}")
                    
                    # Add connection info
                    ig_account['connected_facebook_page'] = {
                        'id': page['id'],
                        'name': page['name']
                    }
                    result['instagram_accounts'].append(ig_account)
                    
                except Exception as e:
                    print(f"Could not fetch Instagram details for page {page['name']}: {e}")
                    # Fallback: use basic Instagram data from page response
                    try:
                        ig_account = page['instagram_business_account'].copy()
                        ig_account['connected_facebook_page'] = {
                            'id': page['id'],
                            'name': page['name']
                        }
                        result['instagram_accounts'].append(ig_account)
                        print(f"Using basic Instagram data for {page['name']}")
                    except Exception as fallback_error:
                        print(f"Could not use fallback Instagram data: {fallback_error}")
        
        result['total_instagram_accounts'] = len(result['instagram_accounts'])
    
    # Get Business Portfolios (Meta Business Suite)
    try:
        portfolios_response = get_user_business_portfolios()
        print("portfolios_response : ")
        print(portfolios_response)
        if 'data' in portfolios_response:
            for business_user in portfolios_response['data']:
                if 'business' in business_user:
                    business = business_user['business']
                    result['business_portfolios'].append(business)
                    business_id = business['id']
                    
                    # Get pages owned by this business portfolio
                    try:
                        business_pages = get_business_portfolio_pages(business_id)
                        if 'data' in business_pages:
                            for page in business_pages['data']:
                                # Get access token for this page
                                try:
                                    page_token_data = get_page_access_token(page['id'])
                                    if 'access_token' in page_token_data:
                                        page['access_token'] = page_token_data['access_token']
                                except Exception as token_error:
                                    print(f"Could not get access token for page {page.get('name', page['id'])}: {token_error}")
                                
                                page['owned_by_business'] = {
                                    'id': business_id,
                                    'name': business['name']
                                }
                                result['business_portfolio_pages'].append(page)
                                
                                # Check for Instagram on business portfolio pages
                                if 'instagram_business_account' in page and page['instagram_business_account']:
                                    ig_account = page['instagram_business_account']
                                    
                                    # Try to get detailed Instagram info if we have page access token
                                    if 'access_token' in page:
                                        try:
                                            ig_details = get_page_connected_instagram_account(page['id'], page['access_token'])
                                            if 'instagram_business_account' in ig_details:
                                                ig_account = ig_details['instagram_business_account']
                                        except Exception as ig_error:
                                            print(f"Could not get detailed Instagram info for business page {page['name']}: {ig_error}")
                                    
                                    ig_account['connected_facebook_page'] = {
                                        'id': page['id'],
                                        'name': page['name']
                                    }
                                    ig_account['owned_by_business'] = {
                                        'id': business_id,
                                        'name': business['name']
                                    }
                                    result['business_portfolio_instagram'].append(ig_account)
                    except Exception as pages_error:
                        print(f"Could not fetch pages for business portfolio {business['name']}: {pages_error}")
                    
                    # Get Instagram accounts directly owned by business portfolio
                    try:
                        business_ig = get_business_portfolio_instagram_accounts(business_id)
                        if 'data' in business_ig:
                            for ig_account in business_ig['data']:
                                ig_account['owned_by_business'] = {
                                    'id': business_id,
                                    'name': business['name']
                                }
                                # Avoid duplicates
                                existing_ids = [ig['id'] for ig in result['business_portfolio_instagram']]
                                if ig_account['id'] not in existing_ids:
                                    result['business_portfolio_instagram'].append(ig_account)
                    except Exception as ig_error:
                        print(f"Could not fetch Instagram accounts for business portfolio {business['name']}: {ig_error}")
            
            result['total_business_portfolios'] = len(result['business_portfolios'])
    except Exception as e:
        print(f"Could not fetch business portfolios: {e}")
    
    # Update total counts
    result['total_pages'] += len(result['business_portfolio_pages'])
    result['total_instagram_accounts'] += len(result['business_portfolio_instagram'])
    
    return result

# ============================================================================
# PERSONAL ACCOUNT FUNCTIONS (Instagram Basic Display API & Facebook Login)
# ============================================================================

def get_personal_instagram_profile(access_token: str = None) -> Dict:
    """
    Get personal Instagram account profile using Instagram Basic Display API.
    
    Args:
        access_token: Instagram Basic Display API access token (optional, uses global if not provided)
        
    Returns:
        Dict containing Instagram profile information
        
    Example:
        profile = get_personal_instagram_profile()
        print(f"Instagram: @{profile.get('username', 'N/A')}")
    """
    token = access_token or INSTAGRAM_BASIC_ACCESS_TOKEN
    if not token:
        return {'error': {'message': 'Instagram Basic Display API access token not configured'}}
    
    url = "https://graph.instagram.com/me"
    params = {
        'fields': 'id,username,account_type,media_count,followers_count,follows_count',
        'access_token': token
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_personal_instagram_media(access_token: str = None, limit: int = 25) -> Dict:
    """
    Get personal Instagram account media using Instagram Basic Display API.
    
    Args:
        access_token: Instagram Basic Display API access token
        limit: Number of media items to retrieve (max 25)
        
    Returns:
        Dict containing Instagram media information
        
    Example:
        media = get_personal_instagram_media()
        for item in media.get('data', []):
            print(f"Media: {item.get('media_type')} - {item.get('caption', 'No caption')}")
    """
    token = access_token or INSTAGRAM_BASIC_ACCESS_TOKEN
    if not token:
        return {'error': {'message': 'Instagram Basic Display API access token not configured'}}
    
    url = "https://graph.instagram.com/me/media"
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp',
        'limit': min(limit, 25),  # Instagram Basic Display API limit
        'access_token': token
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_personal_facebook_profile(access_token: str = None) -> Dict:
    """
    Get personal Facebook profile information.
    
    Args:
        access_token: Facebook user access token (optional, uses main token if not provided)
        
    Returns:
        Dict containing Facebook profile information
        
    Example:
        profile = get_personal_facebook_profile()
        print(f"Facebook: {profile.get('name', 'N/A')}")
    """
    token = access_token or FACEBOOK_USER_ACCESS_TOKEN or ACCESS_TOKEN
    
    url = f"{BASE_URL}/me"
    params = {
        'fields': 'id,name,email,first_name,last_name,picture,cover,birthday,location,hometown',
        'access_token': token
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_personal_facebook_posts(access_token: str = None, limit: int = 25) -> Dict:
    """
    Get personal Facebook posts (requires user_posts permission).
    
    Args:
        access_token: Facebook user access token
        limit: Number of posts to retrieve
        
    Returns:
        Dict containing Facebook posts
        
    Example:
        posts = get_personal_facebook_posts()
        for post in posts.get('data', []):
            print(f"Post: {post.get('message', 'No message')}")
    """
    token = access_token or FACEBOOK_USER_ACCESS_TOKEN or ACCESS_TOKEN
    
    url = f"{BASE_URL}/me/posts"
    params = {
        'fields': 'id,message,story,created_time,type,link,picture',
        'limit': limit,
        'access_token': token
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_personal_facebook_photos(access_token: str = None, limit: int = 25) -> Dict:
    """
    Get personal Facebook photos.
    
    Args:
        access_token: Facebook user access token
        limit: Number of photos to retrieve
        
    Returns:
        Dict containing Facebook photos
        
    Example:
        photos = get_personal_facebook_photos()
        for photo in photos.get('data', []):
            print(f"Photo: {photo.get('name', 'No caption')}")
    """
    token = access_token or FACEBOOK_USER_ACCESS_TOKEN or ACCESS_TOKEN
    
    url = f"{BASE_URL}/me/photos"
    params = {
        'fields': 'id,name,picture,source,created_time,link',
        'limit': limit,
        'access_token': token
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_all_personal_social_accounts(instagram_token: str = None, facebook_token: str = None) -> Dict:
    """
    Get comprehensive information about all personal social media accounts.
    
    Args:
        instagram_token: Instagram Basic Display API token
        facebook_token: Facebook user access token
        
    Returns:
        Dict with all personal social media information
        
    Example:
        accounts = get_all_personal_social_accounts()
        print(f"Personal Instagram: @{accounts['personal_instagram'].get('username', 'N/A')}")
        print(f"Personal Facebook: {accounts['personal_facebook'].get('name', 'N/A')}")
    """
    result = {
        'personal_instagram': {},
        'personal_facebook': {},
        'instagram_media_count': 0,
        'facebook_posts_count': 0,
        'errors': []
    }
    
    # Get personal Instagram
    try:
        ig_profile = get_personal_instagram_profile(instagram_token)
        if 'error' not in ig_profile:
            result['personal_instagram'] = ig_profile
            result['instagram_media_count'] = ig_profile.get('media_count', 0)
        else:
            result['errors'].append(f"Instagram: {ig_profile['error']['message']}")
    except Exception as e:
        result['errors'].append(f"Instagram error: {str(e)}")
    
    # Get personal Facebook
    try:
        fb_profile = get_personal_facebook_profile(facebook_token)
        if 'error' not in fb_profile:
            result['personal_facebook'] = fb_profile
        else:
            result['errors'].append(f"Facebook: {fb_profile['error']['message']}")
    except Exception as e:
        result['errors'].append(f"Facebook error: {str(e)}")
    
    return result

# ============================================================================
# PERSONAL ACCOUNT POSTING FUNCTIONS
# ============================================================================

def post_to_personal_facebook_feed(message: str, access_token: str = None) -> Dict:
    """
    Post a message to personal Facebook timeline (requires publish_to_groups permission).
    Note: Facebook has restricted personal timeline posting for most apps.
    
    Args:
        message: Text message to post
        access_token: Facebook user access token
        
    Returns:
        Dict with post result or error
        
    Example:
        result = post_to_personal_facebook_feed("Hello from my personal account!")
    """
    token = access_token or FACEBOOK_USER_ACCESS_TOKEN or ACCESS_TOKEN
    
    url = f"{BASE_URL}/me/feed"
    data = {
        'message': message,
        'access_token': token
    }
    
    response = requests.post(url, data=data)
    result = response.json()
    
    # Add helpful error context
    if 'error' in result:
        if 'publish_to_groups' in str(result['error']):
            result['error']['help'] = "Personal timeline posting requires 'publish_to_groups' permission and app review"
    
    return result

# ============================================================================
# AUTHENTICATION HELPER FUNCTIONS
# ============================================================================

def generate_instagram_basic_auth_url(app_id: str, redirect_uri: str) -> str:
    """
    Generate Instagram Basic Display API authorization URL.
    
    Args:
        app_id: Your Instagram app ID
        redirect_uri: Your app's redirect URI
        
    Returns:
        Authorization URL for user to visit
        
    Example:
        auth_url = generate_instagram_basic_auth_url("your_app_id", "https://yourapp.com/callback")
        print(f"Visit: {auth_url}")
    """
    base_url = "https://api.instagram.com/oauth/authorize"
    params = {
        'client_id': app_id,
        'redirect_uri': redirect_uri,
        'scope': 'user_profile,user_media',
        'response_type': 'code'
    }
    
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{param_string}"

def exchange_instagram_code_for_token(app_id: str, app_secret: str, redirect_uri: str, code: str) -> Dict:
    """
    Exchange Instagram authorization code for access token.
    
    Args:
        app_id: Your Instagram app ID
        app_secret: Your Instagram app secret
        redirect_uri: Your app's redirect URI
        code: Authorization code from callback
        
    Returns:
        Dict containing access token or error
        
    Example:
        token_data = exchange_instagram_code_for_token(app_id, app_secret, redirect_uri, code)
        if 'access_token' in token_data:
            print(f"Token: {token_data['access_token']}")
    """
    url = "https://api.instagram.com/oauth/access_token"
    data = {
        'client_id': app_id,
        'client_secret': app_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }
    
    response = requests.post(url, data=data)
    return response.json()

def get_long_lived_instagram_token(short_token: str, app_secret: str) -> Dict:
    """
    Exchange short-lived Instagram token for long-lived token (60 days).
    
    Args:
        short_token: Short-lived access token
        app_secret: Your Instagram app secret
        
    Returns:
        Dict containing long-lived token or error
        
    Example:
        long_token = get_long_lived_instagram_token(short_token, app_secret)
        if 'access_token' in long_token:
            print(f"Long-lived token: {long_token['access_token']}")
    """
    url = "https://graph.instagram.com/access_token"
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': app_secret,
        'access_token': short_token
    }
    
    response = requests.get(url, params=params)
    return response.json()

# ============================================================================
# FACEBOOK PAGE POSTING FUNCTIONS
# ============================================================================

def post_text_to_facebook_page(page_id: str, page_access_token: str, text_message: str) -> Dict:
    """
    Post a text-only message to a Facebook page.
    
    Args:
        page_id: Facebook page ID where to post
        page_access_token: Access token for the specific page
        text_message: The text content to post
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = post_text_to_facebook_page("123456", "token", "Hello World!")
        if 'id' in result:
            print(f"Posted successfully: {result['id']}")
    """
    # first get informaitons pages 
    pages_response = get_user_facebook_pages()
    print(f"Full API response: {pages_response}")
    page_access_token = pages_response['data'][0]['access_token']
    url = f"{BASE_URL}/{page_id}/feed"
    data = {
        'message': text_message,
        'access_token': page_access_token
    }
    
    response = requests.post(url, data=data)
    return response.json()

def post_image_to_facebook_page(page_id: str, page_access_token: str, image_url: str, caption: str = "") -> Dict:
    """
    Post an image from URL to a Facebook page with optional caption.
    
    Args:
        page_id: Facebook page ID where to post
        page_access_token: Access token for the specific page
        image_url: Direct URL to the image file
        caption: Optional text caption for the image
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = post_image_to_facebook_page("123456", "token", "https://example.com/image.jpg", "Nice photo!")
    """
    url = f"{BASE_URL}/{page_id}/photos"
    data = {
        'url': image_url,
        'caption': caption,
        'access_token': page_access_token
    }
    
    response = requests.post(url, data=data)
    return response.json()

def upload_local_image_to_facebook_page(page_id: str, page_access_token: str, image_file_path: str, caption: str = "") -> Dict:
    """
    Upload a local image file to a Facebook page with optional caption.
    
    Args:
        page_id: Facebook page ID where to post
        page_access_token: Access token for the specific page
        image_file_path: Local file path to the image
        caption: Optional text caption for the image
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = upload_local_image_to_facebook_page("123456", "token", "/path/to/photo.jpg", "My photo")
    """
    url = f"{BASE_URL}/{page_id}/photos"
    
    try:
        with open(image_file_path, 'rb') as image_file:
            files = {'source': image_file}
            data = {
                'caption': caption,
                'access_token': page_access_token
            }
            
            response = requests.post(url, files=files, data=data)
            return response.json()
    except FileNotFoundError:
        return {'error': {'message': f'Image file not found: {image_file_path}'}}
    except Exception as e:
        return {'error': {'message': f'Failed to upload image: {str(e)}'}}

def post_link_to_facebook_page(page_id: str, page_access_token: str, link_url: str, message: str = "") -> Dict:
    """
    Post a link to a Facebook page with optional message.
    
    Args:
        page_id: Facebook page ID where to post
        page_access_token: Access token for the specific page
        link_url: URL to share
        message: Optional text message to accompany the link
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = post_link_to_facebook_page("123456", "token", "https://example.com", "Check this out!")
    """
    url = f"{BASE_URL}/{page_id}/feed"
    data = {
        'link': link_url,
        'message': message,
        'access_token': page_access_token
    }
    
    response = requests.post(url, data=data)
    return response.json()

def post_text_with_image_to_facebook_page(page_id: str, page_access_token: str, text_message: str, image_url: str) -> Dict:
    """
    Post text message with an image to a Facebook page.
    
    Args:
        page_id: Facebook page ID where to post
        page_access_token: Access token for the specific page
        text_message: Text content to post
        image_url: Direct URL to the image file
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = post_text_with_image_to_facebook_page("123456", "token", "Check this out!", "https://example.com/image.jpg")
    """
    return post_image_to_facebook_page(page_id, page_access_token, image_url, text_message)

# ============================================================================
# INSTAGRAM POSTING FUNCTIONS
# ============================================================================

def post_text_to_instagram_account(instagram_account_id: str, page_access_token: str, text_message: str) -> Dict:
    """
    Post a text-only message to an Instagram business account.
    Note: Instagram requires images for most posts. Text-only posts are limited.
    
    Args:
        instagram_account_id: Instagram business account ID
        page_access_token: Access token from connected Facebook page
        text_message: Text content to post
        
    Returns:
        Dict with creation ID if successful, error details if failed
        
    Example:
        result = post_text_to_instagram_account("ig_123456", "token", "Hello Instagram!")
    """
    # Instagram typically requires media for posts
    # This is mainly for stories or special text posts
    url = f"{BASE_URL}/{instagram_account_id}/media"
    data = {
        'caption': text_message,
        'media_type': 'TEXT',
        'access_token': page_access_token
    }
    
    response = requests.post(url, data=data)
    result = response.json()
    
    # If media creation successful, publish it
    if 'id' in result:
        return publish_instagram_media(instagram_account_id, page_access_token, result['id'])
    
    return result

def post_image_to_instagram_account(instagram_account_id: str, page_access_token: str, image_url: str, caption: str = "") -> Dict:
    """
    Post an image to an Instagram business account with optional caption.
    
    Args:
        instagram_account_id: Instagram business account ID
        page_access_token: Access token from connected Facebook page
        image_url: Direct URL to the image file
        caption: Optional text caption for the image
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = post_image_to_instagram_account("ig_123456", "token", "https://example.com/image.jpg", "Beautiful sunset!")
    """
    print(f"🔍 DEBUG: Creating Instagram media container...")
    print(f"   Instagram ID: {instagram_account_id}")
    print(f"   Image URL: {image_url}")
    print(f"   Caption: {caption}")
    
    pages_response = get_user_facebook_pages()
    print(f"Full API response: {pages_response}")
    page_access_token = pages_response['data'][0]['access_token']
    # Step 1: Create media container
    url = f"{BASE_URL}/{instagram_account_id}/media"
    data = {
        'image_url': image_url,
        'caption': caption,
        'access_token': page_access_token
    }
    
    print(f"   API URL: {url}")
    print(f"   Data: {data}")
    
    response = requests.post(url, data=data)
    result = response.json()
    
    print(f"   Media creation response: {result}")
    
    # Step 2: Publish the media
    if 'id' in result:
        print(f"✅ Media container created with ID: {result['id']}")
        print(f"🚀 Publishing media...")
        publish_result = publish_instagram_media(instagram_account_id, page_access_token, result['id'])
        print(f"   Publish result: {publish_result}")
        return publish_result
    else:
        print(f"❌ Failed to create media container: {result}")
        return result

def upload_local_image_to_instagram_account(instagram_account_id: str, page_access_token: str, image_file_path: str, caption: str = "") -> Dict:
    """
    Upload a local image file to an Instagram business account.
    Note: Instagram API requires images to be accessible via URL, so local upload is more complex.
    
    Args:
        instagram_account_id: Instagram business account ID
        page_access_token: Access token from connected Facebook page
        image_file_path: Local file path to the image
        caption: Optional text caption for the image
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = upload_local_image_to_instagram_account("ig_123456", "token", "/path/to/photo.jpg", "My photo")
    """
    # Instagram API requires images to be accessible via URL
    # For local files, you'd need to upload to a temporary hosting service first
    return {
        'error': {
            'message': 'Instagram API requires images to be accessible via URL. Please upload your image to a web server first and use post_image_to_instagram_account() with the URL.'
        }
    }

def post_text_with_image_to_instagram_account(instagram_account_id: str, page_access_token: str, text_message: str, image_url: str) -> Dict:
    """
    Post text message with an image to an Instagram business account.
    
    Args:
        instagram_account_id: Instagram business account ID
        page_access_token: Access token from connected Facebook page
        text_message: Text content to post as caption
        image_url: Direct URL to the image file
        
    Returns:
        Dict with post ID if successful, error details if failed
        
    Example:
        result = post_text_with_image_to_instagram_account("ig_123456", "token", "Amazing view!", "https://example.com/image.jpg")
    """
    return post_image_to_instagram_account(instagram_account_id, page_access_token, image_url, text_message)

def check_instagram_media_status(creation_id: str, page_access_token: str) -> Dict:
    """
    Check the status of an Instagram media container.
    
    Args:
        creation_id: Media container ID from creation step
        page_access_token: Access token from connected Facebook page
        
    Returns:
        Dict containing media status information
        
    Example:
        status = check_instagram_media_status("creation_123", "token")
        print(f"Status: {status.get('status_code', 'unknown')}")
    """
    url = f"{BASE_URL}/{creation_id}"
    params = {
        'access_token': page_access_token,
        'fields': 'id,status_code,status'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def publish_instagram_media(instagram_account_id: str, page_access_token: str, creation_id: str, max_wait_time: int = 30) -> Dict:
    """
    Publish a previously created Instagram media container.
    Waits for media to be ready before publishing.
    
    Args:
        instagram_account_id: Instagram business account ID
        page_access_token: Access token from connected Facebook page
        creation_id: Media container ID from previous creation step
        max_wait_time: Maximum time to wait for media to be ready (seconds)
        
    Returns:
        Dict with published post ID if successful
        
    Example:
        result = publish_instagram_media("ig_123456", "token", "creation_123")
    """
    print(f"🔍 DEBUG: Publishing Instagram media...")
    print(f"   Instagram ID: {instagram_account_id}")
    print(f"   Creation ID: {creation_id}")
    
    # Wait for media to be ready
    print(f"⏳ Waiting for media to be processed...")
    wait_time = 0
    while wait_time < max_wait_time:
        # Check media status
        status = check_instagram_media_status(creation_id, page_access_token)
        print(f"   Status check ({wait_time}s): {status}")
        
        if 'status_code' in status:
            if status['status_code'] == 'FINISHED':
                print(f"✅ Media is ready for publishing!")
                break
            elif status['status_code'] == 'ERROR':
                return {'error': {'message': f'Media processing failed: {status}'}}
            elif status['status_code'] in ['IN_PROGRESS', 'PUBLISHED']:
                print(f"📊 Media status: {status['status_code']}")
        
        # Wait before next check
        time.sleep(2)
        wait_time += 2
    
    if wait_time >= max_wait_time:
        print(f"⚠️ Timeout waiting for media to be ready, trying to publish anyway...")
    
    # Attempt to publish
    url = f"{BASE_URL}/{instagram_account_id}/media_publish"
    data = {
        'creation_id': creation_id,
        'access_token': page_access_token
    }
    
    print(f"   Publish URL: {url}")
    print(f"   Publish Data: {data}")
    
    response = requests.post(url, data=data)
    result = response.json()
    
    print(f"   Publish response: {result}")
    return result

# ============================================================================
# UTILITY FUNCTIONS FOR AI AGENTS
# ============================================================================

def find_facebook_page_by_name(page_name: str) -> Optional[Dict]:
    """
    Find a specific Facebook page by name from user's accessible pages.
    
    Args:
        page_name: Name of the Facebook page to find (case-insensitive)
        
    Returns:
        Dict with page details if found, None if not found
        
    Example:
        page = find_facebook_page_by_name("My Business Page")
        if page:
            print(f"Found page: {page['name']} (ID: {page['id']})")
    """
    pages_response = get_user_facebook_pages()
    if 'data' in pages_response:
        for page in pages_response['data']:
            if page['name'].lower() == page_name.lower():
                return page
    return None

def find_instagram_account_by_username(username: str) -> Optional[Dict]:
    """
    Find a specific Instagram account by username from user's connected accounts.
    
    Args:
        username: Instagram username to find (without @, case-insensitive)
        
    Returns:
        Dict with Instagram account details if found, None if not found
        
    Example:
        ig_account = find_instagram_account_by_username("mybusiness")
        if ig_account:
            print(f"Found Instagram: @{ig_account['username']}")
    """
    accounts = get_all_user_social_accounts()
    username = username.lower().replace('@', '')
    
    for ig_account in accounts['instagram_accounts']:
        if ig_account['username'].lower() == username:
            return ig_account
    return None

def get_page_access_token_by_page_name(page_name: str) -> Optional[str]:
    """
    Get the access token for a specific Facebook page by name.
    
    Args:
        page_name: Name of the Facebook page
        
    Returns:
        Access token string if page found, None if not found
        
    Example:
        token = get_page_access_token_by_page_name("My Business Page")
        if token:
            post_text_to_facebook_page(page_id, token, "Hello!")
    """
    page = find_facebook_page_by_name(page_name)
    return page['access_token'] if page else None

def post_to_social_media_by_name(platform: str, account_name: str, content_type: str, **kwargs) -> Dict:
    """
    Universal function to post content to social media by account name.
    Perfect for AI agents that need a single interface.
    
    Args:
        platform: "facebook" or "instagram"
        account_name: Name of the Facebook page or Instagram username
        content_type: "text", "image", "text_with_image", or "link"
        **kwargs: Content parameters (text_message, image_url, link_url, caption, etc.)
        
    Returns:
        Dict with post result or error details
        
    Example:
        # Post text to Facebook
        result = post_to_social_media_by_name("facebook", "My Business Page", "text", text_message="Hello!")
        
        # Post image to Instagram
        result = post_to_social_media_by_name("instagram", "mybusiness", "image", image_url="https://...", caption="Nice!")
    """
    try:
        if platform.lower() == "facebook":
            page = find_facebook_page_by_name(account_name)
            if not page:
                return {'error': {'message': f'Facebook page "{account_name}" not found'}}
            
            page_id = page['id']
            page_token = page['access_token']
            
            if content_type == "text":
                return post_text_to_facebook_page(page_id, page_token, kwargs.get('text_message', ''))
            elif content_type == "image":
                return post_image_to_facebook_page(page_id, page_token, kwargs.get('image_url', ''), kwargs.get('caption', ''))
            elif content_type == "text_with_image":
                return post_text_with_image_to_facebook_page(page_id, page_token, kwargs.get('text_message', ''), kwargs.get('image_url', ''))
            elif content_type == "link":
                return post_link_to_facebook_page(page_id, page_token, kwargs.get('link_url', ''), kwargs.get('text_message', ''))
            else:
                return {'error': {'message': f'Unsupported content type: {content_type}'}}
                
        elif platform.lower() == "instagram":
            ig_account = find_instagram_account_by_username(account_name)
            if not ig_account:
                return {'error': {'message': f'Instagram account "@{account_name}" not found'}}
            
            ig_id = ig_account['id']
            page_token = None
            
            # Get the page token from connected Facebook page
            pages_response = get_user_facebook_pages()
            if 'data' in pages_response:
                for page in pages_response['data']:
                    if page['id'] == ig_account['connected_facebook_page']['id']:
                        page_token = page['access_token']
                        break
            
            if not page_token:
                return {'error': {'message': 'Could not find access token for connected Facebook page'}}
            
            if content_type == "text":
                return post_text_to_instagram_account(ig_id, page_token, kwargs.get('text_message', ''))
            elif content_type == "image":
                return post_image_to_instagram_account(ig_id, page_token, kwargs.get('image_url', ''), kwargs.get('caption', ''))
            elif content_type == "text_with_image":
                return post_text_with_image_to_instagram_account(ig_id, page_token, kwargs.get('text_message', ''), kwargs.get('image_url', ''))
            else:
                return {'error': {'message': f'Unsupported content type for Instagram: {content_type}'}}
        else:
            return {'error': {'message': f'Unsupported platform: {platform}'}}
            
    except Exception as e:
        return {'error': {'message': f'Failed to post: {str(e)}'}}

# ============================================================================
# DEMO AND TESTING FUNCTIONS
# ============================================================================

def debug_all_page_access_methods():
    """Comprehensive debug function to test all methods of finding pages"""
    print("\n🔍 COMPREHENSIVE PAGE ACCESS DEBUG:")
    print("=" * 60)
    
    # Method 1: Standard /me/accounts
    print("\n1️⃣ STANDARD /me/accounts:")
    pages_response = get_user_facebook_pages()
    print(f"Response: {pages_response}")
    
    # Method 2: Enhanced /me/accounts with more fields
    print("\n2️⃣ ENHANCED /me/accounts (with perms, higher limit):")
    managed_pages = get_user_managed_pages()
    print(f"Response: {managed_pages}")
    
    # Method 3: Business portfolios
    print("\n3️⃣ BUSINESS PORTFOLIOS (/me/business_users):")
    portfolios = get_user_business_portfolios()
    print(f"Response: {portfolios}")
    
    # Method 4: Alternative businesses endpoint
    print("\n4️⃣ BUSINESSES (/me/businesses):")
    businesses = get_user_businesses()
    print(f"Response: {businesses}")
    
    # Method 5: Search for Observator AI specifically
    print("\n5️⃣ SEARCH FOR 'Observator AI':")
    search_result = search_pages_by_name("Observator AI")
    print(f"Response: {search_result}")
    
    # Method 6: Try to access Observator AI directly by ID (if we know it)
    observator_id = "768301459710923"  # From your previous output
    print(f"\n6️⃣ DIRECT ACCESS TO OBSERVATOR AI (ID: {observator_id}):")
    try:
        direct_access = get_specific_page_info(observator_id)
        print(f"Response: {direct_access}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 7: Try alternative Observator AI ID
    alt_observator_id = "861883367002548"  # From your demo function
    print(f"\n7️⃣ DIRECT ACCESS TO OBSERVATOR AI NEWS (ID: {alt_observator_id}):")
    try:
        alt_direct_access = get_specific_page_info(alt_observator_id)
        print(f"Response: {alt_direct_access}")
    except Exception as e:
        print(f"Error: {e}")

def debug_instagram_connections():
    """Debug function to check Instagram connections in detail"""
    print("\n🔍 DETAILED INSTAGRAM DEBUG:")
    print("=" * 50)
    
    print("\n📋 RAW API RESPONSE:")
    pages_response = get_user_facebook_pages()
    print(f"Full API response: {pages_response}")
    
    if 'data' not in pages_response:
        print("❌ No pages found")
        return
    
    print(f"\n📊 PAGES COUNT: {len(pages_response['data'])}")
    
    for i, page in enumerate(pages_response['data'], 1):
        print(f"\n📄 Page {i}: {page['name']}")
        print(f"   ID: {page['id']}")
        print(f"   Category: {page.get('category', 'N/A')}")
        
        # Check Instagram connection in page response
        if 'instagram_business_account' in page:
            ig_data = page['instagram_business_account']
            if ig_data:
                print(f"   ✅ Instagram connected: {ig_data}")
                print(f"   Instagram ID: {ig_data.get('id', 'N/A')}")
                
                # Try to get detailed Instagram info
                try:
                    ig_details = get_page_connected_instagram_account(page['id'], page['access_token'])
                    print(f"   📊 Detailed Instagram API response:")
                    if 'instagram_business_account' in ig_details:
                        ig_account = ig_details['instagram_business_account']
                        print(f"      Username: @{ig_account.get('username', 'N/A')}")
                        print(f"      Name: {ig_account.get('name', 'N/A')}")
                        print(f"      Followers: {ig_account.get('followers_count', 'N/A')}")
                    else:
                        print(f"      ⚠️ No instagram_business_account in response: {ig_details}")
                except Exception as e:
                    print(f"   ❌ Error getting detailed Instagram info: {e}")
                    
                    # Try direct API call to Instagram account
                    try:
                        ig_id = ig_data.get('id')
                        if ig_id:
                            print(f"   🔄 Trying direct Instagram API call...")
                            ig_url = f"{BASE_URL}/{ig_id}"
                            ig_params = {
                                'access_token': page['access_token'],
                                'fields': 'id,name,username,profile_picture_url,followers_count'
                            }
                            ig_response = requests.get(ig_url, params=ig_params)
                            ig_direct = ig_response.json()
                            print(f"      Direct API response: {ig_direct}")
                    except Exception as direct_error:
                        print(f"   ❌ Direct API call also failed: {direct_error}")
            else:
                print(f"   ❌ Instagram field present but empty")
        else:
            print(f"   ❌ No Instagram connection found")
    
    print(f"\n🔍 TESTING get_all_user_social_accounts():")
    try:
        all_accounts = get_all_user_social_accounts()
        print(f"   Total Instagram accounts found: {all_accounts['total_instagram_accounts']}")
        for ig in all_accounts['instagram_accounts']:
            print(f"   • @{ig.get('username', 'N/A')} connected to {ig.get('connected_facebook_page', {}).get('name', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error in get_all_user_social_accounts(): {e}")

def check_instagram_basic_display_api():
    """Show detailed instructions for setting up personal account access"""
    print("\n📋 PERSONAL ACCOUNT SETUP INSTRUCTIONS:")
    print("=" * 60)
    
    print("\n🔧 TO ACCESS PERSONAL INSTAGRAM (@mamba_happy_world):")
    print("   1. Create Instagram Basic Display App:")
    print("      • Go to https://developers.facebook.com/apps/")
    print("      • Create New App → Consumer → Instagram Basic Display")
    print("      • Add Instagram Basic Display product")
    print("   ")
    print("   2. Configure Instagram Basic Display:")
    print("      • Set Valid OAuth Redirect URIs")
    print("      • Add Instagram Testers (your personal account)")
    print("      • Get App ID and App Secret")
    print("   ")
    print("   3. Generate Access Token:")
    print("      • Use generate_instagram_basic_auth_url() function")
    print("      • User authorizes your app")
    print("      • Exchange code for token with exchange_instagram_code_for_token()")
    print("      • Get long-lived token with get_long_lived_instagram_token()")
    print("   ")
    print("   4. Update Configuration:")
    print("      • Set INSTAGRAM_BASIC_ACCESS_TOKEN in this file")
    print("      • Run demo again to see personal Instagram data")
    
    print("\n🔧 TO ACCESS PERSONAL FACEBOOK POSTS:")
    print("   1. Request Additional Permissions:")
    print("      • user_posts (requires app review)")
    print("      • user_photos")
    print("      • user_videos")
    print("   ")
    print("   2. Facebook Login Flow:")
    print("      • Use Facebook Login for JavaScript SDK")
    print("      • Request permissions during login")
    print("      • Get user access token with required scopes")
    print("   ")
    print("   3. Note: Personal timeline posting is heavily restricted")
    print("      • Most apps cannot post to personal timelines")
    print("      • Requires 'publish_to_groups' permission + app review")
    
    print("\n💡 QUICK START EXAMPLE:")
    print("   # 1. Get Instagram Basic Display auth URL")
    print("   auth_url = generate_instagram_basic_auth_url('YOUR_APP_ID', 'YOUR_REDIRECT_URI')")
    print("   print(f'Visit: {auth_url}')")
    print("   ")
    print("   # 2. After user authorizes, exchange code for token")
    print("   token_data = exchange_instagram_code_for_token(app_id, app_secret, redirect_uri, code)")
    print("   ")
    print("   # 3. Get long-lived token")
    print("   long_token = get_long_lived_instagram_token(token_data['access_token'], app_secret)")
    print("   ")
    print("   # 4. Update INSTAGRAM_BASIC_ACCESS_TOKEN and run demo")
    
    print(f"\n🔗 HELPFUL LINKS:")
    print("   • Instagram Basic Display: https://developers.facebook.com/docs/instagram-basic-display-api")
    print("   • Facebook Login: https://developers.facebook.com/docs/facebook-login")
    print("   • App Dashboard: https://developers.facebook.com/apps/")
    
    if not INSTAGRAM_BASIC_ACCESS_TOKEN:
        print(f"\n⚠️  CURRENT STATUS:")
        print("   • Instagram Basic Display token: NOT CONFIGURED")
        print("   • Personal Instagram access: UNAVAILABLE")
        print("   • Follow setup instructions above to enable personal Instagram access")

def demo_user_information():
    """Demo function to show user information retrieval"""
    print("\n👤 USER INFORMATION DEMO:")
    print("=" * 50)
    
    # Get user profile
    print("\n🔍 Getting user profile...")
    user_profile = get_current_user_profile()
    if 'error' not in user_profile:
        print(f"   ✅ User: {user_profile.get('name', 'N/A')}")
        print(f"   📧 Email: {user_profile.get('email', 'N/A')}")
    else:
        print(f"   ❌ Error: {user_profile['error']['message']}")
        return
    
    # Get all social accounts
    print("\n🔍 Getting all social media accounts...")
    accounts = get_all_user_social_accounts()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Facebook Pages: {accounts['total_pages']}")
    print(f"   Instagram Accounts: {accounts['total_instagram_accounts']}")
    print(f"   Business Portfolios: {accounts['total_business_portfolios']}")
    
    print(f"\n🏢 BUSINESS PORTFOLIOS:")
    for i, portfolio in enumerate(accounts['business_portfolios'], 1):
        print(f"   {i}. {portfolio['name']} (ID: {portfolio['id']})")
        print(f"      Verification: {portfolio.get('verification_status', 'N/A')}")
    
    print(f"\n📄 FACEBOOK PAGES (Personal Access):")
    for i, page in enumerate(accounts['facebook_pages'], 1):
        print(f"   {i}. {page['name']} (ID: {page['id']})")
        print(f"      Category: {page.get('category', 'N/A')}")
        print(f"      Tasks: {', '.join(page.get('tasks', []))}")
    
    print(f"\n📄 FACEBOOK PAGES (Business Portfolio):")
    for i, page in enumerate(accounts['business_portfolio_pages'], 1):
        print(f"   {i}. {page['name']} (ID: {page['id']})")
        print(f"      Category: {page.get('category', 'N/A')}")
        print(f"      Owned by: {page.get('owned_by_business', {}).get('name', 'N/A')}")
        print(f"      Has Access Token: {'Yes' if 'access_token' in page else 'No'}")
    
    print(f"\n📷 INSTAGRAM ACCOUNTS (Personal Access):")
    for i, ig in enumerate(accounts['instagram_accounts'], 1):
        print(f"   {i}. @{ig['username']} ({ig['name']})")
        print(f"      Connected to: {ig['connected_facebook_page']['name']}")
        print(f"      Followers: {ig.get('followers_count', 'N/A')}")
    
    print(f"\n📷 INSTAGRAM ACCOUNTS (Business Portfolio):")
    for i, ig in enumerate(accounts['business_portfolio_instagram'], 1):
        print(f"   {i}. @{ig['username']} ({ig['name']})")
        print(f"      Connected to: {ig.get('connected_facebook_page', {}).get('name', 'N/A')}")
        print(f"      Owned by: {ig.get('owned_by_business', {}).get('name', 'N/A')}")
        print(f"      Followers: {ig.get('followers_count', 'N/A')}")
    
    # Run debug functions
    debug_all_page_access_methods()
    debug_instagram_connections()
    # check_instagram_basic_display_api()

def demo_posting_functions():
    """Demo function to show posting capabilities"""
    print("\n📝 POSTING FUNCTIONS DEMO:")
    print("=" * 50)
    
    # Get first available page for demo
    # pages_response = get_user_facebook_pages()
    # if 'error' in pages_response or not pages_response.get('data'):
    #     print("❌ No Facebook pages available for demo")
    #     return
    
    # page = {'id': '861883367002548', 'name': 'Observator AI News', 'category': 'Société de médias/d’actualités', 'access_token': 'EAAGZAhN3OgkMBP3LEKgPP1D42PdhV9iTy358XSjS97oLDFXpYWOka1ZCL2AEXNVJGbPpmGNI7a9OXc1ETWSSyjQSyXpDes4dNsoZC38uB1n0zF6DdIbB7uZBSSJl6FpPYQxxZBeSG0Sdu60zdodk2aUIKPJvv8CI1Y1jgiumZCEeGylC1vo64ZBIk1af1CzJZBYMY4TOZCnyKaLBfb3cosCdOd1PU5vfNE2KfX1ToH8Cymq0ZD', 'tasks': ['MODERATE', 'MESSAGING', 'ANALYZE', 'ADVERTISE', 'CREATE_CONTENT', 'MANAGE']}
    # page_name = page['name']
    
    # print(f"🎯 Demo target: {page_name}")
    
    # Demo 1: Universal posting function
    # print(f"\n1️⃣ Using universal posting function...")
    # result = post_to_social_media_by_name(
    #     platform="facebook",
    #     account_name=page_name,
    #     content_type="text",
    #     text_message="Hello from the universal posting function! 🚀"
    # )
    
    # if 'id' in result:
    #     print(f"   ✅ Posted successfully: {result['id']}")
    # else:
    #     print(f"   ❌ Failed: {result.get('error', {}).get('message', 'Unknown error')}")
    
    # Demo 2: Direct function call
    # print(f"\n2️⃣ Using direct function call...")
    # result = post_text_to_facebook_page(
    #     page['id'], 
    #     page['access_token'], 
    #     "Hello from direct function call! 📱"
    # )

    # # demo 3 post Image
    # print(f"\n3️⃣ Using direct function call...")
    # result = post_image_to_facebook_page(
    #     page['id'], 
    #     page['access_token'], 
    #     "Hello from direct function call! 📱"
    # )

    # demo 4 local image :
    # print(f"\n4️⃣ Using direct function call...")
    # result = upload_local_image_to_facebook_page(
    #     page['id'], 
    #     page['access_token'], 
    #     image_file_path="/home/yarab/Téléchargements/2919bdf3-2871-47df-998c-22fca9476a21.png",
    #     caption="Hello from direct function call! 📱"
    # )
    
    # demo 5 : insta post
    # print(f"\n5️⃣ Using direct function call...")
    # result = post_text_to_instagram_account(
    #     "17841460715803093", 
    #     "EAAGZAhN3OgkMBP006FVG6YHm9ZBg9kmYNEjLZCf2JX29hbGtAyGXLNFzcxTvuaaAiekI5ZCynLE4L57C3SqGZBBTx9ZAlQTQmeSIVwKou0D2v4Jh1dROrvykDCEdP4q8LZBpWSMs1ZAc19znnYGx67xV9SqC5ubJERUZCfW8TkwAjISfawGbkSYZCsB7LV3ygA0cUVF5tmUZBIoiM5rCbrNp0mdvRNSi715ZBhPZAe9S4VLokkxkZD", 
    #     "Hello from direct function call! 📱"
    # )

    # Get the correct page and Instagram info from your data
    # observator_ai_news = {
    #     'id': '861883367002548',
    #     'name': 'Observator AI News',
    #     'access_token': 'EAAGZAhN3OgkMBP006FVG6YHm9ZBg9kmYNEjLZCf2JX29hbGtAyGXLNFzcxTvuaaAiekI5ZCynLE4L57C3SqGZBBTx9ZAlQTQmeSIVwKou0D2v4Jh1dROrvykDCEdP4q8LZBpWSMs1ZAc19znnYGx67xV9SqC5ubJERUZCfW8TkwAjISfawGbkSYZCsB7LV3ygA0cUVF5tmUZBIoiM5rCbrNp0mdvRNSi715ZBhPZAe9S4VLokkxkZD',
    #     'instagram_business_account': {'id': '17841460715803093'}
    # }
    
    # instagram_id = observator_ai_news['instagram_business_account']['id']
    # page_token = observator_ai_news['access_token']
    
    # print(f"📋 Using Observator AI News Instagram account:")
    # print(f"   Page ID: {observator_ai_news['id']}")
    # print(f"   Instagram ID: {instagram_id}")
    
    # # First, let's get Instagram account details to verify it's accessible
    # print(f"\n🔍 Getting Instagram account details...")
    # ig_details = get_instagram_account_details(instagram_id, page_token)
    # print(f"   Instagram details: {ig_details}")
    
    # # Now try to post
    # result = post_image_to_instagram_account(
    #     instagram_id,
    #     page_token,
    #     "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-sUSNr6dxXNsr0ri9DuQo6GfiNnYlf5irow&s",
    #     "Test post from API! 🚀 #test"
    # )

    # if 'id' in result:
    #     print(f"   ✅ Posted successfully: {result['id']}")
    # else:
    #     print(f"   ❌ Failed: {result.get('error', {}).get('message', 'Unknown error')}")

    # publish to fb : post_text_to_facebook_page
    print(f"\n6️⃣ Using direct function call...")
    result = post_text_to_facebook_page(
        page_id="861883367002548",
        page_access_token="EAAGZAhN3OgkMBP7nBep3LDwnpoxsb9RoZBCYY1bX05zemGDH12XCCNToTmQznFMydDukIzTFkEjbfnO28M4oqz1tuamy3MbqF7UB8aOwg4if1H1YsjeE3sGTuyYknXVDH3Uq8M2COsXLiOK1QclMYkHAPBtKJetUmoIWLtDZA2Ulz2iM3YYwZC6kE9y5jYRKpjfyG1na6UcZCZA98ez3Pq68ZAxMZBjk6oW9Knp0k7itEH4ZD",
        text_message="Hello !"
    )

    if 'id' in result:
        print(f"   ✅ Posted successfully: {result['id']}")
    else:
        print(f"   ❌ Failed: {result.get('error', {}).get('message', 'Unknown error')}")

# def demo_all_features():
#     """Comprehensive demo of all features"""
#     print("🔍 Facebook Graph API - Comprehensive Demo")
#     print("=" * 60)
    
#     demo_user_information()
#     # demo_posting_functions()
    
#     print("\n" + "=" * 60)
#     print("✅ Demo Complete!")

# def main():
#     """Main function - runs user information demo by default"""
#     demo_user_information()

# def demo():
#     """Main function - runs user information demo by default"""
#     demo_posting_functions()

if __name__ == "__main__":
    demo_posting_functions()
    #emo_user_information()
