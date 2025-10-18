"""
Authentication and Authorization Manager
Handles user authentication, API keys, and multi-client support
"""

import jwt
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from threading import Lock
from loguru import logger


@dataclass
class User:
    """User data structure"""
    user_id: str
    username: str
    email: str
    password_hash: str
    api_keys: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIKey:
    """API Key data structure"""
    key_id: str
    user_id: str
    key_hash: str
    name: str
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuthManager:
    """
    Authentication and authorization manager
    Supports JWT tokens, API keys, and multi-client access
    """
    
    def __init__(self, jwt_secret: str = "your-secret-key", jwt_algorithm: str = "HS256"):
        """
        Initialize auth manager
        
        Args:
            jwt_secret: JWT secret key
            jwt_algorithm: JWT algorithm
        """
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        
        self._users: Dict[str, User] = {}
        self._api_keys: Dict[str, APIKey] = {}
        self._lock = Lock()
        
        # Create default admin user
        self._create_default_admin()
        
        logger.info("Auth manager initialized")
    
    def _create_default_admin(self):
        """Create default admin user"""
        try:
            admin_id = "admin"
            if admin_id not in self._users:
                admin_user = User(
                    user_id=admin_id,
                    username="admin",
                    email="admin@example.com",
                    password_hash=self._hash_password("admin123"),
                    metadata={"role": "admin", "is_default": True}
                )
                
                self._users[admin_id] = admin_user
                
                # Create default API key for admin
                api_key = self.create_api_key(
                    user_id=admin_id,
                    name="Default Admin Key",
                    permissions=["*"]  # All permissions
                )
                
                logger.info(f"Created default admin user with API key: {api_key}")
                
        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")
    
    def register_user(self,
                     username: str,
                     email: str,
                     password: str,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Register a new user
        
        Args:
            username: Username
            email: Email address
            password: Password
            metadata: Optional user metadata
            
        Returns:
            str: User ID
        """
        try:
            # Check if username or email already exists
            with self._lock:
                for user in self._users.values():
                    if user.username == username:
                        raise ValueError("Username already exists")
                    if user.email == email:
                        raise ValueError("Email already exists")
                
                # Create user
                user_id = str(uuid.uuid4())
                user = User(
                    user_id=user_id,
                    username=username,
                    email=email,
                    password_hash=self._hash_password(password),
                    metadata=metadata or {}
                )
                
                self._users[user_id] = user
            
            logger.info(f"Registered new user: {username} ({user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user with username/password
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Optional[str]: User ID if authentication successful
        """
        try:
            with self._lock:
                for user in self._users.values():
                    if user.username == username and user.is_active:
                        if self._verify_password(password, user.password_hash):
                            user.last_login = datetime.now()
                            logger.info(f"User authenticated: {username}")
                            return user.user_id
            
            logger.warning(f"Authentication failed for user: {username}")
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def create_jwt_token(self,
                        user_id: str,
                        expires_hours: int = 24,
                        additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create JWT token for user
        
        Args:
            user_id: User identifier
            expires_hours: Token expiration in hours
            additional_claims: Additional JWT claims
            
        Returns:
            str: JWT token
        """
        try:
            user = self._users.get(user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")
            
            # Create JWT payload
            payload = {
                "user_id": user_id,
                "username": user.username,
                "email": user.email,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=expires_hours)
            }
            
            # Add additional claims
            if additional_claims:
                payload.update(additional_claims)
            
            # Generate token
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            logger.info(f"Created JWT token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict]: Token payload if valid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check if user still exists and is active
            user_id = payload.get("user_id")
            user = self._users.get(user_id)
            if not user or not user.is_active:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return None
    
    def create_api_key(self,
                      user_id: str,
                      name: str,
                      permissions: Optional[List[str]] = None,
                      expires_days: Optional[int] = None) -> str:
        """
        Create API key for user
        
        Args:
            user_id: User identifier
            name: API key name
            permissions: List of permissions
            expires_days: Expiration in days (None for no expiration)
            
        Returns:
            str: API key
        """
        try:
            user = self._users.get(user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")
            
            # Generate API key
            key_id = str(uuid.uuid4())
            api_key = f"adk_{uuid.uuid4().hex}"
            key_hash = self._hash_password(api_key)
            
            # Set expiration
            expires_at = None
            if expires_days:
                expires_at = datetime.now() + timedelta(days=expires_days)
            
            # Create API key record
            api_key_record = APIKey(
                key_id=key_id,
                user_id=user_id,
                key_hash=key_hash,
                name=name,
                permissions=permissions or [],
                expires_at=expires_at
            )
            
            with self._lock:
                self._api_keys[key_id] = api_key_record
                user.api_keys.append(key_id)
            
            logger.info(f"Created API key '{name}' for user {user_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify API key
        
        Args:
            api_key: API key to verify
            
        Returns:
            Optional[Dict]: API key info if valid
        """
        try:
            with self._lock:
                for key_record in self._api_keys.values():
                    if not key_record.is_active:
                        continue
                    
                    # Check if key matches
                    if self._verify_password(api_key, key_record.key_hash):
                        # Check expiration
                        if key_record.expires_at and datetime.now() > key_record.expires_at:
                            logger.warning(f"API key {key_record.key_id} expired")
                            return None
                        
                        # Check if user is still active
                        user = self._users.get(key_record.user_id)
                        if not user or not user.is_active:
                            return None
                        
                        # Update last used
                        key_record.last_used = datetime.now()
                        
                        return {
                            "key_id": key_record.key_id,
                            "user_id": key_record.user_id,
                            "username": user.username,
                            "permissions": key_record.permissions,
                            "name": key_record.name
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying API key: {e}")
            return None
    
    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """
        Revoke API key
        
        Args:
            key_id: API key ID
            user_id: User ID (for authorization)
            
        Returns:
            bool: Success status
        """
        try:
            with self._lock:
                key_record = self._api_keys.get(key_id)
                if not key_record:
                    return False
                
                # Check authorization
                if key_record.user_id != user_id:
                    user = self._users.get(user_id)
                    if not user or user.metadata.get("role") != "admin":
                        logger.warning(f"Unauthorized API key revocation attempt by {user_id}")
                        return False
                
                # Revoke key
                key_record.is_active = False
                
                # Remove from user's key list
                user = self._users.get(key_record.user_id)
                if user and key_id in user.api_keys:
                    user.api_keys.remove(key_id)
            
            logger.info(f"Revoked API key {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False
    
    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List API keys for user"""
        try:
            user = self._users.get(user_id)
            if not user:
                return []
            
            keys = []
            with self._lock:
                for key_id in user.api_keys:
                    key_record = self._api_keys.get(key_id)
                    if key_record:
                        keys.append({
                            "key_id": key_record.key_id,
                            "name": key_record.name,
                            "permissions": key_record.permissions,
                            "is_active": key_record.is_active,
                            "created_at": key_record.created_at.isoformat(),
                            "last_used": key_record.last_used.isoformat() if key_record.last_used else None,
                            "expires_at": key_record.expires_at.isoformat() if key_record.expires_at else None
                        })
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    def list_users(self, admin_user_id: str) -> List[Dict[str, Any]]:
        """List all users (admin only)"""
        try:
            # Check if requesting user is admin
            admin_user = self._users.get(admin_user_id)
            if not admin_user or admin_user.metadata.get("role") != "admin":
                logger.warning(f"Unauthorized user list request by {admin_user_id}")
                return []
            
            users = []
            with self._lock:
                for user in self._users.values():
                    users.append({
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat() if user.last_login else None,
                        "api_key_count": len(user.api_keys),
                        "metadata": user.metadata
                    })
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []
    
    def update_user(self,
                   user_id: str,
                   username: Optional[str] = None,
                   email: Optional[str] = None,
                   password: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   requesting_user_id: Optional[str] = None) -> bool:
        """Update user information"""
        try:
            with self._lock:
                user = self._users.get(user_id)
                if not user:
                    return False
                
                # Check authorization
                if requesting_user_id and requesting_user_id != user_id:
                    requesting_user = self._users.get(requesting_user_id)
                    if not requesting_user or requesting_user.metadata.get("role") != "admin":
                        logger.warning(f"Unauthorized user update attempt by {requesting_user_id}")
                        return False
                
                # Update fields
                if username is not None:
                    # Check if username already exists
                    for other_user in self._users.values():
                        if other_user.user_id != user_id and other_user.username == username:
                            raise ValueError("Username already exists")
                    user.username = username
                
                if email is not None:
                    # Check if email already exists
                    for other_user in self._users.values():
                        if other_user.user_id != user_id and other_user.email == email:
                            raise ValueError("Email already exists")
                    user.email = email
                
                if password is not None:
                    user.password_hash = self._hash_password(password)
                
                if metadata is not None:
                    user.metadata.update(metadata)
            
            logger.info(f"Updated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    def deactivate_user(self, user_id: str, admin_user_id: str) -> bool:
        """Deactivate user (admin only)"""
        try:
            # Check if requesting user is admin
            admin_user = self._users.get(admin_user_id)
            if not admin_user or admin_user.metadata.get("role") != "admin":
                logger.warning(f"Unauthorized user deactivation attempt by {admin_user_id}")
                return False
            
            with self._lock:
                user = self._users.get(user_id)
                if user:
                    user.is_active = False
                    
                    # Deactivate all API keys
                    for key_id in user.api_keys:
                        key_record = self._api_keys.get(key_id)
                        if key_record:
                            key_record.is_active = False
            
            logger.info(f"Deactivated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate user: {e}")
            return False
    
    def check_permission(self, user_id: str, permission: str, api_key_info: Optional[Dict] = None) -> bool:
        """
        Check if user has permission
        
        Args:
            user_id: User ID
            permission: Permission to check
            api_key_info: Optional API key info
            
        Returns:
            bool: True if user has permission
        """
        try:
            user = self._users.get(user_id)
            if not user or not user.is_active:
                return False
            
            # Admin users have all permissions
            if user.metadata.get("role") == "admin":
                return True
            
            # Check API key permissions if provided
            if api_key_info:
                permissions = api_key_info.get("permissions", [])
                return "*" in permissions or permission in permissions
            
            # Default permissions for regular users
            default_permissions = [
                "agents:read",
                "agents:create",
                "conversations:read",
                "conversations:create",
                "memory:read",
                "memory:create"
            ]
            
            return permission in default_permissions
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        with self._lock:
            total_users = len(self._users)
            active_users = sum(1 for u in self._users.values() if u.is_active)
            total_api_keys = len(self._api_keys)
            active_api_keys = sum(1 for k in self._api_keys.values() if k.is_active)
            
            # Recent logins (last 24 hours)
            recent_logins = 0
            cutoff = datetime.now() - timedelta(hours=24)
            for user in self._users.values():
                if user.last_login and user.last_login > cutoff:
                    recent_logins += 1
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "total_api_keys": total_api_keys,
                "active_api_keys": active_api_keys,
                "recent_logins_24h": recent_logins
            }
