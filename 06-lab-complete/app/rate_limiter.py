import time
import uuid

from fastapi import HTTPException
from redis import Redis

RATE_WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(self, redis_client: Redis, limit_per_minute: int):
        self.redis = redis_client
        self.limit = limit_per_minute
        self.window = RATE_WINDOW_SECONDS

    def check(self, bucket_key: str):
        now = time.time()
        redis_key = f"rate:{bucket_key}"
        member = f"{now}:{uuid.uuid4().hex}"

        pipe = self.redis.pipeline()
        pipe.zadd(redis_key, {member: now})
        pipe.zremrangebyscore(redis_key, 0, now - self.window)
        pipe.zcard(redis_key)
        pipe.expire(redis_key, self.window + 5)
        _, _, count, _ = pipe.execute()

        if count > self.limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.limit} req/min",
                headers={"Retry-After": str(self.window)},
            )
