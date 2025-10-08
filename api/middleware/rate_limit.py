"""
Rate limiting middleware
"""
from fastapi import Request, HTTPException, status
from typing import Dict, Tuple
from datetime import datetime, timedelta
import logging

from api.config import settings

logger = logging.getLogger(__name__)

# In-memory rate limit store (use Redis in production)
# Format: {identifier: {window_start, request_count}}
rate_limit_store: Dict[str, Tuple[datetime, int]] = {}


class RateLimiter:
    """Simple token bucket rate limiter"""
    
    def __init__(
        self,
        requests: int = None,
        period: int = None
    ):
        """
        Initialize rate limiter
        
        Args:
            requests: Maximum requests per period
            period: Time period in seconds
        """
        self.max_requests = requests or settings.rate_limit_requests
        self.period_seconds = period or settings.rate_limit_period
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the request
        
        Uses API key if present, otherwise IP address
        """
        # Try to get API key from header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key[:16]}"  # Use first 16 chars as identifier
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _clean_old_entries(self):
        """Remove expired entries from store"""
        now = datetime.now()
        expired = [
            key for key, (window_start, _) in rate_limit_store.items()
            if now - window_start > timedelta(seconds=self.period_seconds * 2)
        ]
        for key in expired:
            del rate_limit_store[key]
    
    async def check_rate_limit(self, request: Request) -> Dict[str, any]:
        """
        Check if request is within rate limit
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with rate limit info
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        identifier = self._get_identifier(request)
        now = datetime.now()
        
        # Clean old entries periodically
        if len(rate_limit_store) > 1000:
            self._clean_old_entries()
        
        # Get or create entry
        if identifier not in rate_limit_store:
            rate_limit_store[identifier] = (now, 1)
            return {
                "requests_remaining": self.max_requests - 1,
                "requests_limit": self.max_requests,
                "reset_at": (now + timedelta(seconds=self.period_seconds)).isoformat()
            }
        
        window_start, request_count = rate_limit_store[identifier]
        time_since_start = (now - window_start).total_seconds()
        
        # Reset window if period has passed
        if time_since_start >= self.period_seconds:
            rate_limit_store[identifier] = (now, 1)
            return {
                "requests_remaining": self.max_requests - 1,
                "requests_limit": self.max_requests,
                "reset_at": (now + timedelta(seconds=self.period_seconds)).isoformat()
            }
        
        # Check if limit exceeded
        if request_count >= self.max_requests:
            reset_at = window_start + timedelta(seconds=self.period_seconds)
            retry_after = int((reset_at - now).total_seconds())
            
            logger.warning(f"Rate limit exceeded for {identifier}")
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after_seconds": retry_after,
                    "reset_at": reset_at.isoformat()
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": reset_at.isoformat()
                }
            )
        
        # Increment counter
        rate_limit_store[identifier] = (window_start, request_count + 1)
        
        reset_at = window_start + timedelta(seconds=self.period_seconds)
        
        return {
            "requests_remaining": self.max_requests - (request_count + 1),
            "requests_limit": self.max_requests,
            "reset_at": reset_at.isoformat()
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_dependency(request: Request) -> Dict:
    """
    FastAPI dependency for rate limiting
    
    Usage:
        @app.get("/endpoint", dependencies=[Depends(rate_limit_dependency)])
    """
    return await rate_limiter.check_rate_limit(request)


def get_rate_limit_stats() -> dict:
    """
    Get current rate limit statistics
    
    Returns:
        Dictionary with rate limit stats
    """
    return {
        "active_clients": len(rate_limit_store),
        "max_requests_per_period": settings.rate_limit_requests,
        "period_seconds": settings.rate_limit_period,
        "clients": {
            identifier: {
                "window_start": window_start.isoformat(),
                "request_count": count
            }
            for identifier, (window_start, count) in list(rate_limit_store.items())[:10]
        }
    }