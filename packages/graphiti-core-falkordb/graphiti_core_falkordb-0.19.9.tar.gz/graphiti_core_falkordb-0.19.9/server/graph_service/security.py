"""
Security middleware and utilities for Graphiti server.

Provides authentication, authorization, group access control, and security enforcement.
"""

import hashlib
import hmac
import logging
import os
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from graphiti_core_falkordb.helpers import validate_group_id
from graphiti_core_falkordb.errors import GroupIdValidationError

logger = logging.getLogger(__name__)

# Security configuration from environment
SECURITY_ENABLED = os.getenv('GRAPHITI_SECURITY_ENABLED', 'true').lower() == 'true'
API_KEY = os.getenv('GRAPHITI_API_KEY')
JWT_SECRET = os.getenv('GRAPHITI_JWT_SECRET')
REQUIRE_GROUP_ID = os.getenv('GRAPHITI_REQUIRE_GROUP_ID', 'true').lower() == 'true'
ALLOWED_GROUPS = os.getenv('GRAPHITI_ALLOWED_GROUPS', '').split(',') if os.getenv('GRAPHITI_ALLOWED_GROUPS') else []
RATE_LIMIT_REQUESTS = int(os.getenv('GRAPHITI_RATE_LIMIT_REQUESTS', '100'))
RATE_LIMIT_WINDOW = int(os.getenv('GRAPHITI_RATE_LIMIT_WINDOW', '3600'))  # 1 hour

# Security scheme
security = HTTPBearer(auto_error=False)


class SecurityConfig(BaseModel):
    """Security configuration model."""
    security_enabled: bool = SECURITY_ENABLED
    require_group_id: bool = REQUIRE_GROUP_ID
    allowed_groups: List[str] = ALLOWED_GROUPS
    rate_limit_requests: int = RATE_LIMIT_REQUESTS
    rate_limit_window: int = RATE_LIMIT_WINDOW


class UserContext(BaseModel):
    """User context for authenticated requests."""
    user_id: str
    allowed_groups: Set[str]
    is_admin: bool = False
    rate_limit_key: str


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        
        # Clean old requests
        if key in self._requests:
            self._requests[key] = [req_time for req_time in self._requests[key] 
                                 if now - req_time < window]
        else:
            self._requests[key] = []
        
        # Check limit
        if len(self._requests[key]) >= limit:
            return False
        
        # Add current request
        self._requests[key].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def verify_api_key(api_key: str) -> bool:
    """Verify API key using secure comparison."""
    if not API_KEY:
        return False
    return hmac.compare_digest(api_key, API_KEY)


def extract_user_context(credentials: HTTPAuthorizationCredentials) -> UserContext:
    """Extract user context from credentials."""
    # For API key authentication
    if credentials.scheme.lower() == "bearer":
        if verify_api_key(credentials.credentials):
            # For now, API key gives admin access to all groups
            # In production, you'd decode JWT or lookup user permissions
            return UserContext(
                user_id="api_key_user",
                allowed_groups=set(ALLOWED_GROUPS) if ALLOWED_GROUPS else set(),
                is_admin=True,
                rate_limit_key=f"api_key:{hashlib.sha256(credentials.credentials.encode()).hexdigest()[:8]}"
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserContext]:
    """Get current authenticated user context."""
    if not SECURITY_ENABLED:
        # Security disabled - allow all operations
        return UserContext(
            user_id="anonymous",
            allowed_groups=set(),
            is_admin=True,
            rate_limit_key=f"ip:{request.client.host if request.client else 'unknown'}"
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return extract_user_context(credentials)


async def enforce_rate_limit(user: UserContext = Depends(get_current_user)):
    """Enforce rate limiting."""
    if not rate_limiter.is_allowed(
        user.rate_limit_key, 
        RATE_LIMIT_REQUESTS, 
        RATE_LIMIT_WINDOW
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds"
        )


def enforce_group_id_required(group_id: Optional[str]) -> str:
    """Enforce that group_id is provided and valid."""
    if REQUIRE_GROUP_ID and (not group_id or group_id.strip() == ''):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group_id is required for data isolation. Please provide a valid group_id."
        )
    
    if group_id:
        try:
            validate_group_id(group_id)
        except GroupIdValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    return group_id or ''


def enforce_group_access(group_id: str, user: UserContext):
    """Enforce that user has access to the specified group."""
    if not SECURITY_ENABLED or user.is_admin:
        return
    
    # If allowed_groups is configured and not empty, enforce it
    if ALLOWED_GROUPS and group_id not in user.allowed_groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to group '{group_id}'. User does not have permission."
        )


async def security_dependency(
    request: Request,
    user: UserContext = Depends(get_current_user)
) -> UserContext:
    """Combined security dependency for all protected endpoints."""
    # Rate limiting
    await enforce_rate_limit(user)
    
    return user


def validate_and_authorize_group(
    group_id: Optional[str],
    user: UserContext
) -> str:
    """Validate group_id and check user authorization."""
    # Enforce group_id requirement
    validated_group_id = enforce_group_id_required(group_id)
    
    # Enforce group access
    if validated_group_id:
        enforce_group_access(validated_group_id, user)
    
    return validated_group_id


class SecurityHeaders:
    """Security headers middleware."""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


def get_security_config() -> SecurityConfig:
    """Get current security configuration."""
    return SecurityConfig()


def log_security_event(event_type: str, details: Dict, user_id: str = "unknown"):
    """Log security events for monitoring."""
    logger.warning(f"SECURITY_EVENT: {event_type} - User: {user_id} - Details: {details}")


# Dependency for endpoints that need group validation
async def validate_group_access(
    group_id: str,
    user: UserContext = Depends(security_dependency)
) -> str:
    """Dependency to validate group access for path parameters."""
    return validate_and_authorize_group(group_id, user)


# Dependency for endpoints that need optional group validation
async def validate_optional_group_access(
    group_id: Optional[str],
    user: UserContext = Depends(security_dependency)
) -> str:
    """Dependency to validate optional group access."""
    return validate_and_authorize_group(group_id, user)
