"""
Authentication middleware for API key validation
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import secrets
import hashlib
from datetime import datetime
import logging

from api.config import settings

logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-memory API key store (use database in production)
# Format: {hashed_key: {created_at, name, usage_count}}
api_keys_store = {}


def generate_api_key(name: str = "default") -> str:
    """
    Generate a new API key
    
    Args:
        name: Name/label for the API key
        
    Returns:
        API key string
    """
    # Generate random key
    random_part = secrets.token_urlsafe(32)
    api_key = f"{settings.api_key_prefix}{random_part}"
    
    # Hash and store
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    api_keys_store[key_hash] = {
        "created_at": datetime.now(),
        "name": name,
        "usage_count": 0,
        "last_used": None
    }
    
    logger.info(f"Generated new API key: {name}")
    
    return api_key


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage/comparison"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    key_hash = hash_api_key(api_key)
    
    if key_hash in api_keys_store:
        # Update usage stats
        api_keys_store[key_hash]["usage_count"] += 1
        api_keys_store[key_hash]["last_used"] = datetime.now()
        return True
    
    return False


async def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Dependency to validate API key from request header
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include 'X-API-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return api_key


# Optional: Dependency for endpoints that don't require auth
async def get_optional_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[str]:
    """
    Optional API key dependency - doesn't raise error if missing
    
    Useful for endpoints that have different behavior for authenticated users
    """
    if api_key and validate_api_key(api_key):
        return api_key
    return None


def list_api_keys() -> dict:
    """
    List all API keys (hashed) with metadata
    
    Returns:
        Dictionary of API keys and their metadata
    """
    return {
        key_hash[:16] + "...": {
            "name": data["name"],
            "created_at": data["created_at"].isoformat(),
            "usage_count": data["usage_count"],
            "last_used": data["last_used"].isoformat() if data["last_used"] else None
        }
        for key_hash, data in api_keys_store.items()
    }


def revoke_api_key(api_key: str) -> bool:
    """
    Revoke an API key
    
    Args:
        api_key: API key to revoke
        
    Returns:
        True if revoked, False if not found
    """
    key_hash = hash_api_key(api_key)
    
    if key_hash in api_keys_store:
        del api_keys_store[key_hash]
        logger.info(f"Revoked API key: {key_hash[:16]}...")
        return True
    
    return False


# Generate a default API key for development
if settings.api_reload:  # Only in development mode
    default_key = generate_api_key("development")
    logger.info(f"🔑 Development API Key: {default_key}")
    logger.info("Add this to your requests: -H 'X-API-Key: {key}'")