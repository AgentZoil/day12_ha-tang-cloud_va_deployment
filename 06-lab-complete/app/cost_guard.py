from datetime import datetime

from fastapi import HTTPException
from redis import Redis


class CostGuard:
    def __init__(self, redis_client: Redis, monthly_budget_usd: float):
        self.redis = redis_client
        self.budget = monthly_budget_usd

    def _key(self) -> str:
        return f"cost:{datetime.utcnow():%Y-%m}"

    def record_cost(self, amount_usd: float) -> float:
        if amount_usd <= 0:
            return self.current_spend()

        key = self._key()
        total = self.redis.incrbyfloat(key, amount_usd)
        self.redis.expire(key, 60 * 60 * 24 * 40)

        if total > self.budget:
            raise HTTPException(
                status_code=503,
                detail="Monthly budget exhausted. Try again next month.",
            )
        return total

    def current_spend(self) -> float:
        value = self.redis.get(self._key())
        return float(value) if value else 0.0
