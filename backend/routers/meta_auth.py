"""
Meta Authentication Router
Handles Facebook/Instagram authentication token management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from loguru import logger

from auth.dependencies import get_current_user
from tools.meta.meta_publisher_tool import update_meta_tokens, get_active_tokens

router = APIRouter(prefix="/api/v1/meta", tags=["Meta Authentication"])


class MetaTokensRequest(BaseModel):
    """Request model for updating Meta tokens"""
    user_access_token: str
    page_access_token: str
    page_id: str
    instagram_account_id: Optional[str] = None


class MetaTokensResponse(BaseModel):
    """Response model for Meta tokens operations"""
    success: bool
    message: str
    page_id: Optional[str] = None
    instagram_account_id: Optional[str] = None
    updated_at: Optional[float] = None
    error: Optional[str] = None


@router.post("/tokens", response_model=MetaTokensResponse)
async def update_tokens(
    tokens: MetaTokensRequest,
    current_user: dict = Depends(get_current_user)
) -> MetaTokensResponse:
    """
    Update Meta authentication tokens for publishing.
    
    Args:
        tokens: Meta tokens data from frontend
        current_user: Current authenticated user
        
    Returns:
        MetaTokensResponse with update status
    """
    try:
        logger.info(f"🔄 Updating Meta tokens for user {current_user.get('username', 'unknown')}")
        logger.info(f"   Page ID: {tokens.page_id}")
        logger.info(f"   Instagram ID: {tokens.instagram_account_id}")
        
        # Update tokens using the tool function
        result = update_meta_tokens(
            user_access_token=tokens.user_access_token,
            page_access_token=tokens.page_access_token,
            page_id=tokens.page_id,
            instagram_account_id=tokens.instagram_account_id
        )
        
        if result["success"]:
            logger.info("✅ Meta tokens updated successfully via API")
            return MetaTokensResponse(
                success=True,
                message=result["message"],
                page_id=result["page_id"],
                instagram_account_id=result["instagram_account_id"],
                updated_at=result["updated_at"]
            )
        else:
            logger.error(f"❌ Meta token update failed: {result.get('error', 'Unknown error')}")
            return MetaTokensResponse(
                success=False,
                message=result["message"],
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        logger.error(f"❌ Meta token update API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update Meta tokens: {str(e)}"
        )


@router.get("/tokens/status")
async def get_tokens_status(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current Meta tokens status.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict with current token status
    """
    try:
        logger.info(f"📊 Getting Meta tokens status for user {current_user.get('username', 'unknown')}")
        
        # Get active tokens
        tokens = get_active_tokens()
        
        return {
            "success": True,
            "has_tokens": bool(tokens["page_access_token"]),
            "page_id": tokens.get("page_id"),
            "instagram_account_id": tokens.get("instagram_account_id"),
            "message": "Tokens status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Meta tokens status error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tokens status: {str(e)}"
        )


@router.delete("/tokens")
async def clear_tokens(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear stored Meta tokens.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict with clear operation status
    """
    try:
        logger.info(f"🗑️ Clearing Meta tokens for user {current_user.get('username', 'unknown')}")
        
        # Clear tokens by updating with empty values
        result = update_meta_tokens(
            user_access_token="",
            page_access_token="",
            page_id="",
            instagram_account_id=""
        )
        
        return {
            "success": True,
            "message": "Meta tokens cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Meta tokens clear error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear tokens: {str(e)}"
        )


@router.post("/test-connection")
async def test_meta_connection(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Test Meta API connection with current tokens.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict with connection test results
    """
    try:
        logger.info(f"🧪 Testing Meta connection for user {current_user.get('username', 'unknown')}")
        
        # Import the account info function
        from tools.meta_publisher_tool import meta_get_account_info
        
        # Test connection
        result = meta_get_account_info()
        
        return {
            "success": result["success"],
            "message": "Connection test completed",
            "facebook_status": result["facebook"]["status"],
            "instagram_status": result["instagram"]["status"],
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        logger.error(f"❌ Meta connection test error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )
