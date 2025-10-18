"""
Authentication API Router
Handles authentication endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger

from auth.auth_manager import AuthManager
from auth.dependencies import get_current_user


router = APIRouter()


def get_auth_manager() -> AuthManager:
    """Dependency to get auth manager"""
    from main import managers
    return managers["auth_manager"]


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class CreateAPIKeyRequest(BaseModel):
    name: str
    permissions: list = ["*"]
    expires_days: int = None


@router.post("/login")
async def login(
    request: LoginRequest,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Login and get JWT token"""
    try:
        user_id = auth_manager.authenticate_user(request.username, request.password)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = auth_manager.create_jwt_token(user_id)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/register")
async def register(
    request: RegisterRequest,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Register new user"""
    try:
        user_id = auth_manager.register_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api-keys")
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Create API key"""
    try:
        api_key = auth_manager.create_api_key(
            user_id=current_user["user_id"],
            name=request.name,
            permissions=request.permissions,
            expires_days=request.expires_days
        )
        
        return {
            "success": True,
            "message": "API key created successfully",
            "api_key": api_key
        }
        
    except Exception as e:
        logger.error(f"API key creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api-keys")
async def list_api_keys(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """List user's API keys"""
    try:
        api_keys = auth_manager.list_api_keys(current_user["user_id"])
        
        return {
            "success": True,
            "api_keys": api_keys
        }
        
    except Exception as e:
        logger.error(f"API key listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "success": True,
        "user": current_user
    }
