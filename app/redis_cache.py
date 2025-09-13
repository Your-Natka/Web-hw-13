import json
import redis
from app.config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def cache_user(user):
    key = f"user:{user.id}"
    r.setex(key, 3600, json.dumps({"id": user.id, "email": user.email, "is_verified": user.is_verified}))

def get_cached_user(user_id):
    v = r.get(f"user:{user_id}")
    if v:
        return json.loads(v)
    return None

def delete_cached_user(user_id):
    r.delete(f"user:{user_id}")
