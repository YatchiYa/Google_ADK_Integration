/**
 * Facebook Authentication Service
 * Handles Facebook OAuth flow, token management, and API interactions
 */

declare global {
  interface Window {
    FB: any;
    fbAsyncInit: () => void;
  }
}

export interface FacebookUser {
  id: string;
  name: string;
  email?: string;
  picture?: {
    data: {
      url: string;
    };
  };
}

export interface FacebookPage {
  id: string;
  name: string;
  access_token: string;
  category: string;
  tasks: string[];
  instagram_business_account?: {
    id: string;
  };
}

export interface FacebookTokens {
  accessToken: string;
  expiresIn: number;
  signedRequest: string;
  userID: string;
}

export interface FacebookAuthState {
  isConnected: boolean;
  user: FacebookUser | null;
  pages: FacebookPage[];
  accessToken: string | null;
  tokenExpiry: number | null;
  lastRefresh: number | null;
}

class FacebookServiceClass {
  private appId: string;
  private version: string = 'v19.0';
  private isInitialized: boolean = false;
  private authState: FacebookAuthState = {
    isConnected: false,
    user: null,
    pages: [],
    accessToken: null,
    tokenExpiry: null,
    lastRefresh: null,
  };

  // Required permissions for Meta publishing
  private readonly REQUIRED_PERMISSIONS = [
    // User permissions
    'public_profile',
    'email',
    'user_likes',
    'user_events',
    'user_photos',
    'user_videos',
    'user_posts',
    'user_messenger_contact',
    
    // Page permissions
    'pages_show_list',
    'pages_manage_posts',
    'pages_read_engagement',
    'pages_manage_metadata',
    'pages_read_user_content',
    'pages_manage_engagement',
    'pages_manage_instant_articles',
    'page_events',
    'read_insights',
    
    // Instagram permissions
    'instagram_basic',
    'instagram_content_publish',
    'instagram_branded_content_brand',
    'instagram_branded_content_creator',
    'instagram_branded_content_ads_brand',
    'instagram_manage_events',
    
    // Business permissions
    'business_management',
    'ads_management',
    'ads_read',
    'manage_app_solution'
  ];

  constructor() {
    // Get Facebook App ID from environment or use your App ID
    this.appId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID || '450270912741955';
    console.log('🔧 Facebook App ID:', this.appId);
    this.initializeFacebookSDK();
  }

  /**
   * Initialize Facebook SDK
   */
  private initializeFacebookSDK(): void {
    if (typeof window === 'undefined') return;

    // UPDATE: Check if we're on HTTPS or localhost
    const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost';
    
    if (!isSecure) {
      console.warn('⚠️ Facebook SDK requires HTTPS. Please use https://localhost:3000 or run npm run dev:https');
      return;
    }

    // Load Facebook SDK
    window.fbAsyncInit = () => {
      window.FB.init({
        appId: this.appId,
        cookie: true,
        xfbml: true,
        version: this.version,
      });

      this.isInitialized = true;
      console.log('✅ Facebook SDK initialized');
      
      // UPDATE: Check existing login status only on HTTPS
      if (window.location.protocol === 'https:') {
        this.checkLoginStatus();
      }
    };

    // Load SDK script
    if (!document.getElementById('facebook-jssdk')) {
      const script = document.createElement('script');
      script.id = 'facebook-jssdk';
      script.src = 'https://connect.facebook.net/en_US/sdk.js';
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    }
  }

  /**
   * Wait for SDK to be ready
   */
  private waitForSDK(): Promise<void> {
    return new Promise((resolve) => {
      if (this.isInitialized && window.FB) {
        resolve();
        return;
      }

      const checkSDK = () => {
        if (this.isInitialized && window.FB) {
          resolve();
        } else {
          setTimeout(checkSDK, 100);
        }
      };
      checkSDK();
    });
  }

  /**
   * Check current login status
   */
  async checkLoginStatus(): Promise<FacebookAuthState> {
    await this.waitForSDK();

    return new Promise((resolve) => {
      window.FB.getLoginStatus((response: any) => {
        console.log('Facebook login status:', response);
        
        if (response.status === 'connected') {
          this.handleLoginSuccess(response.authResponse);
        } else {
          this.authState.isConnected = false;
          this.authState.user = null;
          this.authState.accessToken = null;
        }
        
        resolve(this.authState);
      });
    });
  }

  /**
   * Login to Facebook with required permissions
   */
  async login(): Promise<FacebookAuthState> {
    await this.waitForSDK();

    return new Promise((resolve, reject) => {
      window.FB.login((response: any) => {
        console.log('Facebook login response:', response);
        
        if (response.status === 'connected') {
          this.handleLoginSuccess(response.authResponse);
          resolve(this.authState);
        } else {
          const error = response.status === 'not_authorized' 
            ? 'User denied permissions' 
            : 'Login failed';
          reject(new Error(error));
        }
      }, { 
        scope: this.REQUIRED_PERMISSIONS.join(','),
        return_scopes: true 
      });
    });
  }

  /**
   * Handle successful login
   */
  private async handleLoginSuccess(authResponse: FacebookTokens): Promise<void> {
    this.authState.accessToken = authResponse.accessToken;
    this.authState.tokenExpiry = Date.now() + (authResponse.expiresIn * 1000);
    this.authState.lastRefresh = Date.now();
    this.authState.isConnected = true;

    // Store tokens in localStorage
    localStorage.setItem('facebook_auth', JSON.stringify({
      accessToken: authResponse.accessToken,
      tokenExpiry: this.authState.tokenExpiry,
      userID: authResponse.userID,
    }));

    try {
      // Get user info
      await this.getUserInfo();
      
      // Get user pages
      await this.getUserPages();
      
      console.log('✅ Facebook authentication complete:', this.authState);
    } catch (error) {
      console.error('❌ Error completing Facebook authentication:', error);
    }
  }

  /**
   * Get user information
   */
  private async getUserInfo(): Promise<void> {
    await this.waitForSDK();

    return new Promise((resolve, reject) => {
      window.FB.api('/me', { fields: 'id,name,email,picture' }, (response: any) => {
        if (response.error) {
          reject(new Error(response.error.message));
          return;
        }

        this.authState.user = response;
        resolve();
      });
    });
  }

  /**
   * Get user's Facebook pages with access tokens
   */
  private async getUserPages(): Promise<void> {
    await this.waitForSDK();

    return new Promise((resolve, reject) => {
      console.log('🔍 Fetching user pages...');
      
      window.FB.api('/me/accounts', { 
        fields: 'id,name,access_token,category,tasks,instagram_business_account,picture' 
      }, (response: any) => {
        console.log('📄 Raw pages response:', response);
        
        if (response.error) {
          console.error('❌ Pages API error:', response.error);
          reject(new Error(response.error.message));
          return;
        }

        this.authState.pages = response.data || [];
        console.log('📄 Facebook pages loaded:', this.authState.pages.length, 'pages');
        
        // Log each page for debugging
        this.authState.pages.forEach((page, index) => {
          console.log(`📄 Page ${index + 1}:`, {
            id: page.id,
            name: page.name,
            category: page.category,
            hasAccessToken: !!page.access_token,
            hasInstagram: !!page.instagram_business_account,
            tasks: page.tasks?.length || 0
          });
        });
        
        resolve();
      });
    });
  }

  /**
   * Logout from Facebook
   */
  async logout(): Promise<void> {
    await this.waitForSDK();

    return new Promise((resolve) => {
      window.FB.logout(() => {
        this.authState = {
          isConnected: false,
          user: null,
          pages: [],
          accessToken: null,
          tokenExpiry: null,
          lastRefresh: null,
        };

        // Clear localStorage
        localStorage.removeItem('facebook_auth');
        
        console.log('✅ Facebook logout complete');
        resolve();
      });
    });
  }

  /**
   * Check if token needs refresh (refresh if expires in less than 1 hour)
   */
  private needsTokenRefresh(): boolean {
    if (!this.authState.tokenExpiry) return false;
    
    const oneHour = 60 * 60 * 1000;
    return (this.authState.tokenExpiry - Date.now()) < oneHour;
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string | null> {
    if (!this.authState.isConnected || !this.needsTokenRefresh()) {
      return this.authState.accessToken;
    }

    try {
      await this.waitForSDK();

      return new Promise((resolve, reject) => {
        window.FB.getLoginStatus((response: any) => {
          if (response.status === 'connected') {
            this.handleLoginSuccess(response.authResponse);
            resolve(this.authState.accessToken);
          } else {
            // Token expired, need to re-login
            this.authState.isConnected = false;
            reject(new Error('Token expired, re-login required'));
          }
        });
      });
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      return null;
    }
  }

  /**
   * Get current authentication state
   */
  getAuthState(): FacebookAuthState {
    return { ...this.authState };
  }

  /**
   * Get access token for a specific page
   */
  getPageAccessToken(pageId: string): string | null {
    const page = this.authState.pages.find(p => p.id === pageId);
    return page?.access_token || null;
  }

  /**
   * Get Instagram account ID for a specific page
   */
  getInstagramAccountId(pageId: string): string | null {
    const page = this.authState.pages.find(p => p.id === pageId);
    return page?.instagram_business_account?.id || null;
  }

  /**
   * Find page by name
   */
  findPageByName(pageName: string): FacebookPage | null {
    return this.authState.pages.find(p => 
      p.name.toLowerCase() === pageName.toLowerCase()
    ) || null;
  }

  /**
   * Get tokens for Meta publisher tools
   */
  getMetaPublisherTokens(): {
    userAccessToken: string | null;
    pageAccessToken: string | null;
    instagramAccountId: string | null;
    pageId: string | null;
  } {
    // Use the first page as default (you can modify this logic)
    const defaultPage = this.authState.pages[0];
    
    return {
      userAccessToken: this.authState.accessToken,
      pageAccessToken: defaultPage?.access_token || null,
      instagramAccountId: defaultPage?.instagram_business_account?.id || null,
      pageId: defaultPage?.id || null,
    };
  }

  /**
   * Check if user has required permissions
   */
  async checkPermissions(): Promise<{ granted: string[]; missing: string[] }> {
    await this.waitForSDK();

    return new Promise((resolve, reject) => {
      window.FB.api('/me/permissions', (response: any) => {
        if (response.error) {
          reject(new Error(response.error.message));
          return;
        }

        const granted = response.data
          .filter((perm: any) => perm.status === 'granted')
          .map((perm: any) => perm.permission);

        const missing = this.REQUIRED_PERMISSIONS.filter(
          perm => !granted.includes(perm)
        );

        resolve({ granted, missing });
      });
    });
  }

  /**
   * Request additional permissions
   */
  async requestPermissions(permissions: string[]): Promise<boolean> {
    await this.waitForSDK();

    return new Promise((resolve) => {
      window.FB.login((response: any) => {
        resolve(response.status === 'connected');
      }, { 
        scope: permissions.join(','),
        auth_type: 'rerequest'
      });
    });
  }

  /**
   * Initialize from stored tokens (call on app startup)
   */
  async initializeFromStorage(): Promise<boolean> {
    const stored = localStorage.getItem('facebook_auth');
    if (!stored) return false;

    try {
      const { accessToken, tokenExpiry, userID } = JSON.parse(stored);
      
      // Check if token is still valid
      if (Date.now() > tokenExpiry) {
        localStorage.removeItem('facebook_auth');
        return false;
      }

      // Verify token with Facebook
      const status = await this.checkLoginStatus();
      return status.isConnected;
    } catch (error) {
      console.error('❌ Error initializing from storage:', error);
      localStorage.removeItem('facebook_auth');
      return false;
    }
  }
}

export const FacebookService = new FacebookServiceClass();
export default FacebookService;
