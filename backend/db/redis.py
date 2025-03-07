import redis.asyncio as redis
from config import Config

token_blocklist = redis.from_url(Config.REDIS_URL)
async def add_jti_to_blocklist(jti: str):
    await token_blocklist.set(
        name=jti,
        value="",
        ex=3600  # Expiration time in seconds
    )

async def token_in_blocklist(jti: str):
    jti_value = await token_blocklist.get(jti)
    return jti_value is not None  # Returns True if token exists in blocklist


