const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  expires_in: number;
}

export interface ApiKeyResponse {
  api_key: string;
  name: string;
  permissions: string[];
  created_at: string;
}

class AuthServiceClass {
  private apiKey: string | null = null;
  private userId: string | null = null;

  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data: LoginResponse = await response.json();
    
    // Store user ID
    this.userId = data.user_id;
    localStorage.setItem('user_id', data.user_id);
    
    // Create API key
    await this.createApiKey(data.access_token);
    
    return data;
  }

  private async createApiKey(jwtToken: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/api-keys`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'Frontend Client',
        permissions: ['*']
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create API key');
    }

    const data: ApiKeyResponse = await response.json();
    this.apiKey = data.api_key;
    localStorage.setItem('api_key', data.api_key);
  }

  async checkAuth(): Promise<boolean> {
    // Check if we have stored credentials
    const storedApiKey = localStorage.getItem('api_key');
    const storedUserId = localStorage.getItem('user_id');
    
    if (storedApiKey && storedUserId) {
      this.apiKey = storedApiKey;
      this.userId = storedUserId;
      
      // Verify the API key is still valid
      try {
        const response = await fetch(`${API_BASE_URL}/health`, {
          headers: {
            'X-API-Key': storedApiKey,
          },
        });
        
        return response.ok;
      } catch {
        return false;
      }
    }
    
    return false;
  }

  getApiKey(): string | null {
    return this.apiKey || localStorage.getItem('api_key');
  }

  getUserId(): string | null {
    return this.userId || localStorage.getItem('user_id');
  }

  logout(): void {
    this.apiKey = null;
    this.userId = null;
    localStorage.removeItem('api_key');
    localStorage.removeItem('user_id');
  }

  getAuthHeaders(): Record<string, string> {
    const apiKey = this.getApiKey();
    if (!apiKey) {
      throw new Error('No API key available');
    }
    
    return {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json',
    };
  }
}

export const AuthService = new AuthServiceClass();
