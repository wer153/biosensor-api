import os
import json
import secrets
from datetime import datetime, timedelta
from uuid import UUID
from redis.asyncio import Redis
from typing import Dict, Any, Optional


class RedisTokenService:
    """Redis-based refresh token management service"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.prefix = "refresh_token:"
        self.user_prefix = "user_tokens:"
    
    async def _connect(self):
        """Initialize Redis connection"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    async def create_refresh_token(
        self, 
        user_id: UUID, 
        expires_in_hours: int = 1
    ) -> str:
        """Create a new refresh token for user"""
        if not self.redis:
            await self._connect()
            
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        token_data = {
            "user_id": str(user_id),
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        await self.redis.setex(
            f"{self.prefix}{token}",
            int(timedelta(hours=expires_in_hours).total_seconds()),
            json.dumps(token_data)
        )
        
        return token
    
    async def _get_token_data(self, token: str) -> Dict[str, Any] | None:
        """Get token data if valid"""
        if not self.redis:
            await self._connect()
            
        token_json = await self.redis.get(f"{self.prefix}{token}")
        if not token_json:
            return None
            
        return json.loads(token_json)
    
    async def validate_refresh_token(self, token: str) -> UUID | None:
        """Validate refresh token and return user ID if valid"""
        token_data = await self._get_token_data(token)
        if not token_data:
            return None
        return UUID(token_data["user_id"])

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


token_service = RedisTokenService()

# TODO: improve connection handling regarding memory leaks
