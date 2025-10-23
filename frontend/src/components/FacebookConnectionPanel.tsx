"use client";

import { useState, useEffect } from 'react';
import { FacebookService, FacebookAuthState } from '@/services/facebook.service';
import FacebookLoginButton from './FacebookLoginButton';
import { ChatService } from '@/services/chat.service';
import { FaFacebook, FaInstagram, FaCheck, FaExclamationTriangle, FaSync, FaRocket } from 'react-icons/fa';

interface FacebookConnectionPanelProps {
  agentId: string;
  sessionId?: string;
  onConnectionChange?: (connected: boolean) => void;
  className?: string;
}

export default function FacebookConnectionPanel({
  agentId,
  sessionId,
  onConnectionChange,
  className = ''
}: FacebookConnectionPanelProps) {
  const [authState, setAuthState] = useState<FacebookAuthState>({
    isConnected: false,
    user: null,
    pages: [],
    accessToken: null,
    tokenExpiry: null,
    lastRefresh: null,
  });
  const [selectedPageId, setSelectedPageId] = useState<string>('');
  const [syncingTokens, setSyncingTokens] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<Date | null>(null);

  useEffect(() => {
    // Initialize Facebook auth state
    const initAuth = async () => {
      const state = await FacebookService.checkLoginStatus();
      setAuthState(state);
      onConnectionChange?.(state.isConnected);
      
      // Auto-select first page if available
      if (state.pages.length > 0 && !selectedPageId) {
        setSelectedPageId(state.pages[0].id);
      }
    };
    
    initAuth();
  }, []);

  const handleAuthChange = (newAuthState: FacebookAuthState) => {
    setAuthState(newAuthState);
    onConnectionChange?.(newAuthState.isConnected);
    
    // Auto-select first page if available
    if (newAuthState.pages.length > 0 && !selectedPageId) {
      setSelectedPageId(newAuthState.pages[0].id);
    }
    
    // Auto-sync tokens when connected
    if (newAuthState.isConnected && newAuthState.pages.length > 0) {
      syncTokensWithAgent();
    }
  };

  const syncTokensWithAgent = async () => {
    if (!authState.isConnected || !selectedPageId || !sessionId) {
      console.log('Cannot sync: missing requirements', {
        connected: authState.isConnected,
        pageId: selectedPageId,
        sessionId
      });
      return;
    }

    try {
      setSyncingTokens(true);
      setSyncError(null);

      const selectedPage = authState.pages.find(p => p.id === selectedPageId);
      if (!selectedPage) {
        throw new Error('Selected page not found');
      }

      // Prepare token data
      const tokenData = {
        user_access_token: authState.accessToken!,
        page_access_token: selectedPage.access_token,
        page_id: selectedPage.id,
        instagram_account_id: selectedPage.instagram_business_account?.id || null
      };

      console.log('🔄 Syncing tokens with agent:', tokenData);

      // Send tokens to backend API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/meta/tokens`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
        body: JSON.stringify(tokenData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to sync tokens');
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Token sync failed');
      }

      setLastSync(new Date());
      console.log('✅ Tokens synced successfully');
      
    } catch (error) {
      console.error('❌ Token sync failed:', error);
      setSyncError(error instanceof Error ? error.message : 'Token sync failed');
    } finally {
      setSyncingTokens(false);
    }
  };

  const handlePageChange = (pageId: string) => {
    setSelectedPageId(pageId);
    // Auto-sync when page changes
    if (authState.isConnected && sessionId) {
      setTimeout(() => syncTokensWithAgent(), 500);
    }
  };

  const selectedPage = authState.pages.find(p => p.id === selectedPageId);

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 space-y-4 ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        <FaFacebook className="h-5 w-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900">Facebook Connection</h3>
        {authState.isConnected && (
          <div className="ml-auto flex items-center gap-1 text-green-600 text-sm">
            <FaCheck className="h-3 w-3" />
            <span>Connected</span>
          </div>
        )}
      </div>

      {/* Facebook Login */}
      <FacebookLoginButton
        onAuthChange={handleAuthChange}
        onError={(error) => setSyncError(error)}
        size="sm"
        variant="outline"
        showStatus={false}
      />

      {/* Page Selection */}
      {authState.isConnected && authState.pages.length > 0 && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Page for Publishing
            </label>
            <select
              value={selectedPageId}
              onChange={(e) => handlePageChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a page...</option>
              {authState.pages.map(page => (
                <option key={page.id} value={page.id}>
                  {page.name} {page.instagram_business_account ? '📷' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Selected Page Info */}
          {selectedPage && (
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Selected Page:</span>
                <span className="text-sm text-gray-900">{selectedPage.name}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Category:</span>
                <span className="text-sm text-gray-600">{selectedPage.category}</span>
              </div>

              {selectedPage.instagram_business_account && (
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 flex items-center gap-1">
                    <FaInstagram className="h-3 w-3 text-pink-600" />
                    Instagram:
                  </span>
                  <span className="text-sm text-green-600">Connected</span>
                </div>
              )}

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Permissions:</span>
                <span className="text-sm text-gray-600">{selectedPage.tasks.length} granted</span>
              </div>
            </div>
          )}

          {/* Sync Button */}
          <div className="flex items-center gap-2">
            <button
              onClick={syncTokensWithAgent}
              disabled={syncingTokens || !selectedPageId || !sessionId}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm rounded-md transition-colors"
            >
              {syncingTokens ? (
                <FaSync className="h-3 w-3 animate-spin" />
              ) : (
                <FaRocket className="h-3 w-3" />
              )}
              <span>{syncingTokens ? 'Syncing...' : 'Sync with Agent'}</span>
            </button>
            
            {lastSync && (
              <span className="text-xs text-gray-500">
                Last sync: {lastSync.toLocaleTimeString()}
              </span>
            )}
          </div>

          {/* Sync Error */}
          {syncError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-700 text-sm">
                <FaExclamationTriangle className="h-4 w-4" />
                <span className="font-medium">Sync Error</span>
              </div>
              <div className="text-xs text-red-600 mt-1">{syncError}</div>
              <button
                onClick={() => setSyncError(null)}
                className="text-xs text-red-600 hover:text-red-800 mt-2 underline"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Help Text */}
          <div className="text-xs text-gray-500 bg-blue-50 rounded-lg p-3">
            <div className="font-medium text-blue-800 mb-1">💡 How it works:</div>
            <div className="space-y-1">
              <div>1. Connect your Facebook account above</div>
              <div>2. Select the page you want to publish to</div>
              <div>3. Click "Sync with Agent" to enable publishing</div>
              <div>4. Your agent can now post to Facebook and Instagram!</div>
            </div>
          </div>
        </div>
      )}

      {/* No Pages Warning */}
      {authState.isConnected && authState.pages.length === 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
          <div className="flex items-center gap-2 text-orange-700 text-sm">
            <FaExclamationTriangle className="h-4 w-4" />
            <span className="font-medium">No Pages Found</span>
          </div>
          <div className="text-xs text-orange-600 mt-1">
            You need to have Facebook pages to publish content. Create a page on Facebook first.
          </div>
        </div>
      )}
    </div>
  );
}
