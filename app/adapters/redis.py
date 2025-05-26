from redis import asyncio as redis

from app.config.config import RedisConfig


class RedisAdapter:
    def __init__(self, config: RedisConfig):
        self.redis = redis.from_url(url=config.dsn)

    async def get(self, key: str) -> str | None:
        value = await self.redis.get(name=key)
        if value:
            return value.decode("utf-8")

    async def set(self, key: str, value: str, delay: int = None) -> None:
        await self.redis.set(name=key, value=value, ex=delay)

    async def set_many(self, values: dict[str, str]) -> None:
        for key, value in values.items():
            await self.redis.set(name=key, value=value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def keys(self, pattern: str, **kwargs) -> list[str]:
        resp = await self.redis.keys(pattern=pattern, **kwargs)
        return [i.decode() for i in resp]
