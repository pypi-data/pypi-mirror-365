"""Authentication module following LangConnect pattern."""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client
from gotrue.types import User

from .config import settings


security = HTTPBearer()


def get_supabase_user(jwt_token: str) -> User:
    """Validate JWT token with Supabase and return user.
    
    Args:
        jwt_token: JWT token string to validate
        
    Returns:
        User: A Supabase User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
    response = supabase.auth.get_user(jwt_token)
    user = response.user
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token or user not found")
    return user

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """Get current authenticated user from credentials.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User: Authenticated Supabase user
        
    Raises:
        HTTPException: If authentication fails
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    try:
        user = get_supabase_user(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
# NOTE: For development mode we use a mock user to circumvent auth requirements
class DevUser:
    """Mock user for development mode that mimics Supabase User interface."""
    def __init__(self):
        self.id = "00000000-0000-0000-0000-000000000000"
        self.email = "dev@localhost"


def get_dev_user() -> DevUser:
    return DevUser()
