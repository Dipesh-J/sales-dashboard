import json
import hashlib
import logging
from functools import wraps
from typing import Optional

import redis

from .config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None
_redis_available: bool = False


def init_redis() -> None:
    """Initialize Redis connection. Fails silently — app works without Redis."""
    global _redis_client, _redis_available
    try:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        _redis_client.ping()
        _redis_available = True
        logger.info("Redis cache connected at %s", settings.REDIS_URL)
    except Exception as e:
        _redis_client = None
        _redis_available = False
        logger.warning("Redis unavailable (%s) — caching disabled", e)


def get_redis() -> Optional[redis.Redis]:
    return _redis_client if _redis_available else None


# ── Key helpers ──

CACHE_PREFIX = "sd:"  # sales-dashboard namespace

# TTLs in seconds
TTL_DASHBOARD = 300   # 5 min for dashboard queries
TTL_FILTERS = 600     # 10 min for filter lists


def _build_key(namespace: str, params: dict) -> str:
    """Build a deterministic cache key from namespace + sorted params."""
    filtered = {k: v for k, v in sorted(params.items()) if v is not None}
    raw = f"{namespace}:{json.dumps(filtered, sort_keys=True)}"
    short_hash = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"{CACHE_PREFIX}{namespace}:{short_hash}"


def cache_get(key: str):
    """Get value from cache. Returns None on miss or if Redis unavailable."""
    if not _redis_available:
        return None
    try:
        val = _redis_client.get(key)
        if val is not None:
            return json.loads(val)
    except Exception as e:
        logger.debug("Cache get error: %s", e)
    return None


def cache_set(key: str, value, ttl: int = TTL_DASHBOARD) -> None:
    """Set value in cache with TTL. Fails silently."""
    if not _redis_available:
        return
    try:
        _redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.debug("Cache set error: %s", e)


def invalidate_all() -> None:
    """Delete all dashboard cache keys (called after data upload)."""
    if not _redis_available:
        return
    try:
        cursor = 0
        while True:
            cursor, keys = _redis_client.scan(cursor, match=f"{CACHE_PREFIX}*", count=200)
            if keys:
                _redis_client.delete(*keys)
            if cursor == 0:
                break
        logger.info("Cache invalidated")
    except Exception as e:
        logger.debug("Cache invalidate error: %s", e)


def cached(namespace: str, ttl: int = TTL_DASHBOARD):
    """Decorator for endpoint functions. Caches the return value keyed on all
    non-db, non-file parameters.

    Usage:
        @cached("sales_total")
        def get_total_sales(dateRange=None, brand=None, ..., db=...):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Build params dict excluding db session and file objects
            cache_params = {k: v for k, v in kwargs.items() if k != "db" and k != "file"}
            key = _build_key(namespace, cache_params)

            hit = cache_get(key)
            if hit is not None:
                return hit

            result = fn(*args, **kwargs)
            cache_set(key, result, ttl)
            return result
        return wrapper
    return decorator
