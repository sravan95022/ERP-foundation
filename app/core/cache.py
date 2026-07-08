import time
import functools

# In-memory cache used for local/dev. In production, swap the two functions
# below for redis.get/redis.set calls against settings.REDIS_URL — the
# call sites (the `cached` decorator) don't need to change.
_store: dict[str, tuple[float, object]] = {}


def cache_get(key: str):
    entry = _store.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if time.time() > expires_at:
        del _store[key]
        return None
    return value


def cache_set(key: str, value, ttl_seconds: int = 60):
    _store[key] = (time.time() + ttl_seconds, value)


def cached(ttl_seconds: int = 60):
    """Decorator for caching a function's return value by its arguments."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            hit = cache_get(key)
            if hit is not None:
                return hit
            result = func(*args, **kwargs)
            cache_set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator
