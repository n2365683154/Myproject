"""
楚然智考系统 - Redis客户端模块
用于验证码存储、缓存等功能
支持Redis不可用时使用内存缓存
"""
import time
import redis.asyncio as redis
from typing import Optional, Dict, Any
from app.config import settings


class MemoryCache:
    """内存缓存，Redis不可用时的备用方案"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expires: Dict[str, float] = {}
    
    def _is_expired(self, key: str) -> bool:
        if key in self._expires:
            return time.time() > self._expires[key]
        return False
    
    def _cleanup(self, key: str):
        if self._is_expired(key):
            self._cache.pop(key, None)
            self._expires.pop(key, None)
    
    async def set(self, key: str, value: str, expire: int = None) -> bool:
        self._cache[key] = value
        if expire:
            self._expires[key] = time.time() + expire
        return True
    
    async def get(self, key: str) -> Optional[str]:
        self._cleanup(key)
        return self._cache.get(key)
    
    async def delete(self, key: str) -> int:
        deleted = 1 if key in self._cache else 0
        self._cache.pop(key, None)
        self._expires.pop(key, None)
        return deleted
    
    async def exists(self, key: str) -> bool:
        self._cleanup(key)
        return key in self._cache
    
    async def ttl(self, key: str) -> int:
        if key in self._expires:
            remaining = self._expires[key] - time.time()
            return max(0, int(remaining))
        return -1
    
    async def incr(self, key: str) -> int:
        val = int(self._cache.get(key, 0)) + 1
        self._cache[key] = str(val)
        return val
    
    async def expire(self, key: str, seconds: int) -> bool:
        if key in self._cache:
            self._expires[key] = time.time() + seconds
            return True
        return False


class RedisClient:
    """Redis客户端封装类，支持降级到内存缓存"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._memory_cache = MemoryCache()
        self._use_memory = True  # 默认使用内存缓存，连接成功后切换
        self._connected = False
    
    async def connect(self):
        """建立Redis连接"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            await self.redis.ping()
            self._use_memory = False
            self._connected = True
            print("Redis连接成功")
        except Exception as e:
            print(f"Redis连接失败，使用内存缓存: {e}")
            self._use_memory = True
            self._connected = True
    
    async def disconnect(self):
        """关闭Redis连接"""
        if self.redis and not self._use_memory:
            await self.redis.close()
    
    async def set(self, key: str, value: str, expire: int = None) -> bool:
        if self._use_memory:
            return await self._memory_cache.set(key, value, expire)
        try:
            if expire:
                return await self.redis.setex(key, expire, value)
            return await self.redis.set(key, value)
        except:
            return await self._memory_cache.set(key, value, expire)
    
    async def get(self, key: str) -> Optional[str]:
        if self._use_memory:
            return await self._memory_cache.get(key)
        try:
            return await self.redis.get(key)
        except:
            return await self._memory_cache.get(key)
    
    async def delete(self, key: str) -> int:
        if self._use_memory:
            return await self._memory_cache.delete(key)
        try:
            return await self.redis.delete(key)
        except:
            return await self._memory_cache.delete(key)
    
    async def exists(self, key: str) -> bool:
        if self._use_memory:
            return await self._memory_cache.exists(key)
        try:
            return await self.redis.exists(key)
        except:
            return await self._memory_cache.exists(key)
    
    async def ttl(self, key: str) -> int:
        if self._use_memory:
            return await self._memory_cache.ttl(key)
        try:
            return await self.redis.ttl(key)
        except:
            return await self._memory_cache.ttl(key)
    
    async def incr(self, key: str) -> int:
        if self._use_memory:
            return await self._memory_cache.incr(key)
        try:
            return await self.redis.incr(key)
        except:
            return await self._memory_cache.incr(key)
    
    async def expire(self, key: str, seconds: int) -> bool:
        if self._use_memory:
            return await self._memory_cache.expire(key, seconds)
        try:
            return await self.redis.expire(key, seconds)
        except:
            return await self._memory_cache.expire(key, seconds)


# 全局Redis客户端实例
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """获取Redis客户端的依赖注入函数"""
    return redis_client
