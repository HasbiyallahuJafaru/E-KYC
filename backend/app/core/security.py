"""
Security and authentication utilities.
Handles API key validation, rate limiting, and JWT tokens.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.models.api_client import ApiClient
from app.core.exceptions import AuthenticationError, RateLimitExceededError


settings = get_settings()
security = HTTPBearer()


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key pair.
    
    Returns:
        tuple: (raw_key, hashed_key)
        - raw_key: The key to show the user (only shown once)
        - hashed_key: The hashed version to store in database
    """
    # Generate 32-byte random key
    raw_key = secrets.token_urlsafe(32)
    
    # Hash for storage (SHA-256)
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    
    return raw_key, hashed_key


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    """
    Verify API key against stored hash.
    
    Args:
        raw_key: The raw key from request
        hashed_key: The stored hash from database
        
    Returns:
        bool: True if valid, False otherwise
    """
    computed_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return secrets.compare_digest(computed_hash, hashed_key)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token for internal dashboard users.
    
    Args:
        data: Payload to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


async def get_api_client(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> ApiClient:
    """
    FastAPI dependency to validate API key and retrieve client.
    
    Used for external API authentication.
    
    Args:
        credentials: HTTP bearer token from request
        db: Database session
        
    Returns:
        ApiClient: The authenticated client
        
    Raises:
        AuthenticationError: If API key is invalid or client inactive
    """
    raw_key = credentials.credentials
    
    # Query all active clients and check key
    # Note: In production with many clients, consider adding an index on api_key_hash
    clients = db.query(ApiClient).filter(
        ApiClient.is_active == True
    ).all()
    
    authenticated_client = None
    for client in clients:
        if verify_api_key(raw_key, client.api_key_hash):
            authenticated_client = client
            break
    
    if not authenticated_client:
        raise AuthenticationError("Invalid API key")
    
    # Check rate limit using Redis
    # This is a placeholder - actual implementation below
    await check_rate_limit(authenticated_client.id)
    
    return authenticated_client


async def check_rate_limit(client_id: str) -> None:
    """
    Check if client has exceeded rate limit using token bucket algorithm.
    
    Args:
        client_id: The client identifier
        
    Raises:
        RateLimitExceededError: If rate limit exceeded
        
    Note:
        Rate limit configuration:
        - Free tier: 100 requests/hour
        - Basic tier: 1000 requests/hour
        - Premium tier: 10000 requests/hour
    """
    # TODO: Implement Redis-based token bucket
    # For now, allow all requests
    # 
    # Implementation plan:
    # 1. Get client tier from database
    # 2. Determine rate limit based on tier
    # 3. Use Redis INCR with TTL for sliding window
    # 4. Raise RateLimitExceededError if exceeded
    pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    FastAPI dependency for internal dashboard JWT authentication.
    
    Args:
        credentials: HTTP bearer token from request
        db: Database session
        
    Returns:
        dict: User information from token
        
    Raises:
        AuthenticationError: If token is invalid
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    # Validate required fields
    if "sub" not in payload:  # sub = user_id
        raise AuthenticationError("Invalid token payload")
    
    return payload


def require_permissions(*required_permissions: str):
    """
    Decorator for endpoints requiring specific permissions.
    
    Args:
        required_permissions: Permission strings required
        
    Returns:
        Dependency that checks permissions
    """
    async def permission_checker(
        user: dict = Depends(get_current_user)
    ) -> dict:
        user_permissions = user.get("permissions", [])
        
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required permission: {permission}"
                )
        
        return user
    
    return permission_checker
