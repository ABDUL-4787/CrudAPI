import os
import json
import redis
from typing import Optional, List

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=3
    )
except Exception as e:
    print(f"Warning: Redis client setup failed: {e}")
    redis_client = None

CACHE_TTL = 3600  # 1 hour in seconds

def get_cached_tasks(user_id: int) -> Optional[List[dict]]:
    if redis_client is None:
        return None
    try:
        cached_data = redis_client.get(f"tasks:user:{user_id}")
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        print(f"Warning: Cache read operation failed: {e}")
    return None

def set_cached_tasks(user_id: int, tasks: List[dict]) -> None:
    if redis_client is None:
        return
    try:
        redis_client.setex(
            name=f"tasks:user:{user_id}",
            time=CACHE_TTL,
            value=json.dumps(tasks)
        )
    except Exception as e:
        print(f"Warning: Cache write operation failed: {e}")

def invalidate_cached_tasks(user_id: int) -> None:
    if redis_client is None:
        return
    try:
        redis_client.delete(f"tasks:user:{user_id}")
    except Exception as e:
        print(f"Warning: Cache delete operation failed: {e}")
