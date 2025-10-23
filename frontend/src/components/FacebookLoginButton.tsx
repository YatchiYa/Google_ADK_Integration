"use client";

import { useState, useEffect } from 'react';
import { FacebookService, FacebookAuthState } from '@/services/facebook.service';
import { FaFacebook, FaSpinner, FaCheck, FaExclamationTriangle, FaSignOutAlt } from 'react-icons/fa';

interface FacebookLoginButtonProps {
  onAuthChange?: (authState: FacebookAuthState) => void;
  onError?: (error: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'outline' | 'minimal';
  showStatus?: boolean;
  autoConnect?: boolean;
}

export default function FacebookLoginButton({
  onAuthChange,
  onError,
  className = '',
  size = 'md',
  variant = 'primary',
  showStatus = true,
  autoConnect = false
}: FacebookLoginButtonProps) {
  const [authState, setAuthState] = useState<FacebookAuthState>({
    isConnected: false,
    user: null,
    pages: [],
    accessToken: null,
    tokenExpiry: null,
    lastRefresh: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permissions, setPermissions] = useState<{ granted: string[]; missing: string[] } | null>(null);

  useEffect(() => {
    initializeAuth();
  }, []);

  useEffect(() => {
    if (autoConnect && !authState.isConnected && !loading) {
      handleLogin();
    }
  }, [autoConnect, authState.isConnected, loading]);

  const initializeAuth = async () => {
    try {
      setLoading(true);
      
      // Try to initialize from stored tokens
      const initialized = await FacebookService.initializeFromStorage();
      
      if (initialized) {
        const state = FacebookService.getAuthState();
        setAuthState(state);
        onAuthChange?.(state);
        
        // Check permissions
        await checkPermissions();
      } else {
        // Check current login status
        const state = await FacebookService.checkLoginStatus();
        setAuthState(state);
        onAuthChange?.(state);
        
        if (state.isConnected) {
          await checkPermissions();
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to initialize Facebook auth';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const checkPermissions = async () => {
    try {
      const perms = await FacebookService.checkPermissions();
      setPermissions(perms);
      
      if (perms.missing.length > 0) {
        console.warn('⚠️ Missing Facebook permissions:', perms.missing);
      }
    } catch (err) {
      console.error('❌ Error checking permissions:', err);
    }
  };

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const state = await FacebookService.login();
      setAuthState(state);
      onAuthChange?.(state);
      
      // Check permissions after login
      await checkPermissions();
      
      console.log('✅ Facebook login successful:', state);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Facebook login failed';
      setError(errorMsg);
      onError?.(errorMsg);
      console.error('❌ Facebook login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await FacebookService.logout();
      const state = FacebookService.getAuthState();
      setAuthState(state);
      setPermissions(null);
      onAuthChange?.(state);
      
      console.log('✅ Facebook logout successful');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Facebook logout failed';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestPermissions = async () => {
    if (!permissions?.missing.length) return;
    
    try {
      setLoading(true);
      const success = await FacebookService.requestPermissions(permissions.missing);
      
      if (success) {
        await checkPermissions();
        const state = FacebookService.getAuthState();
        setAuthState(state);
        onAuthChange?.(state);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to request permissions';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  // Variant classes
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600',
    outline: 'bg-transparent hover:bg-blue-50 text-blue-600 border-blue-600 border-2',
    minimal: 'bg-transparent hover:bg-blue-50 text-blue-600 border-transparent'
  };

  const baseClasses = `
    inline-flex items-center justify-center gap-2 rounded-lg font-medium
    transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  `;

  if (authState.isConnected) {
    return (
      <div className={`space-y-3 ${className}`}>
        {/* Connected Status */}
        <div className={`${baseClasses} ${sizeClasses[size]} bg-green-50 text-green-700 border border-green-200`}>
          <FaCheck className="h-4 w-4" />
          <span>Connected as {authState.user?.name}</span>
        </div>

        {/* Status Information */}
        {showStatus && (
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Pages:</span>
              <span className="font-medium">{authState.pages.length}</span>
            </div>
            
            {permissions && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Permissions:</span>
                <span className={`font-medium ${permissions.missing.length > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                  {permissions.granted.length}/{permissions.granted.length + permissions.missing.length}
                </span>
              </div>
            )}
            
            {authState.pages.length > 0 && (
              <div className="mt-2">
                <div className="text-xs text-gray-500 mb-1">Connected Pages:</div>
                {authState.pages.slice(0, 3).map(page => (
                  <div key={page.id} className="text-xs text-gray-700 flex items-center gap-2">
                    <span>📄</span>
                    <span>{page.name}</span>
                    {page.instagram_business_account && <span className="text-pink-600">📷</span>}
                  </div>
                ))}
                {authState.pages.length > 3 && (
                  <div className="text-xs text-gray-500">+{authState.pages.length - 3} more</div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Missing Permissions Warning */}
        {permissions && permissions.missing.length > 0 && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-orange-700 text-sm mb-2">
              <FaExclamationTriangle className="h-4 w-4" />
              <span className="font-medium">Missing Permissions</span>
            </div>
            <div className="text-xs text-orange-600 mb-2">
              Some features may not work without these permissions:
            </div>
            <div className="text-xs text-orange-600 mb-3">
              {permissions.missing.join(', ')}
            </div>
            <button
              onClick={handleRequestPermissions}
              disabled={loading}
              className="text-xs bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded-md transition-colors"
            >
              {loading ? <FaSpinner className="animate-spin h-3 w-3" /> : 'Grant Permissions'}
            </button>
          </div>
        )}

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          disabled={loading}
          className={`${baseClasses} ${sizeClasses.sm} bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300`}
        >
          {loading ? (
            <FaSpinner className="animate-spin h-4 w-4" />
          ) : (
            <FaSignOutAlt className="h-4 w-4" />
          )}
          <span>Disconnect</span>
        </button>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Login Button */}
      <button
        onClick={handleLogin}
        disabled={loading}
        className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]}`}
      >
        {loading ? (
          <FaSpinner className="animate-spin h-5 w-5" />
        ) : (
          <FaFacebook className="h-5 w-5" />
        )}
        <span>Connect Facebook</span>
      </button>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center gap-2 text-red-700 text-sm">
            <FaExclamationTriangle className="h-4 w-4" />
            <span className="font-medium">Connection Error</span>
          </div>
          <div className="text-xs text-red-600 mt-1">{error}</div>
          <button
            onClick={() => setError(null)}
            className="text-xs text-red-600 hover:text-red-800 mt-2 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Help Text */}
      {showStatus && (
        <div className="text-xs text-gray-500">
          Connect your Facebook account to publish content to your pages and Instagram accounts.
        </div>
      )}
    </div>
  );
}
