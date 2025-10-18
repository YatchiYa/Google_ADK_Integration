"""
Authentication Dependencies
FastAPI dependencies for authentication and authorization
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger


security = HTTPBearer(auto_error=False)


def get_auth_manager():
    """Get auth manager from global managers"""
    from main import managers
    return managers["auth_manager"]


async def get_current_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
    auth_manager = Depends(get_auth_manager)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token or API key
    
    Returns:
        Dict containing user information
    """
    try:
        # Try API key authentication first
        if x_api_key:
            api_key_info = auth_manager.verify_api_key(x_api_key)
            if api_key_info:
                return {
                    "user_id": api_key_info["user_id"],
                    "username": api_key_info["username"],
                    "auth_method": "api_key",
                    "permissions": api_key_info["permissions"],
                    "api_key_info": api_key_info
                }
        
        # Try JWT token authentication
        if authorization and authorization.credentials:
            token_payload = auth_manager.verify_jwt_token(authorization.credentials)
            if token_payload:
                return {
                    "user_id": token_payload["user_id"],
                    "username": token_payload["username"],
                    "email": token_payload["email"],
                    "auth_method": "jwt",
                    "token_payload": token_payload
                }
        
        # No valid authentication found
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_permission(user_info: Dict[str, Any], permission: str) -> bool:
    """
    Check if user has required permission
    
    Args:
        user_info: User information from get_current_user
        permission: Required permission
        
    Returns:
        bool: True if user has permission
    """
    try:
        from main import managers
        auth_manager = managers["auth_manager"]
        
        api_key_info = user_info.get("api_key_info")
        return auth_manager.check_permission(
            user_info["user_id"],
            permission,
            api_key_info
        )
        
    except Exception as e:
        logger.error(f"Permission check error: {e}")
        return False


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require admin privileges
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Dict: User information if admin
    """
    if not require_permission(current_user, "admin:*"):
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    
    return current_user


# Optional authentication (allows anonymous access)
async def get_optional_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
    auth_manager = Depends(get_auth_manager)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, None otherwise
    Used for endpoints that work with or without authentication
    """
    try:
        return await get_current_user(authorization, x_api_key, auth_manager)
    except HTTPException:
        return None
