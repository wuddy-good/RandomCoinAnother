from redis.asyncio import Redis

redis = Redis()


async def get_user_locale(user_id: int):
    result = await redis.get(f"user_locale:{user_id}")
    if result:
        return result.decode("utf-8")
    return result


async def set_user_locale(user_id: int, locale: str):
    await redis.set(f"user_locale:{user_id}", locale)


async def get_channel_message_id(lottery_id: int):
    result = await redis.get(f"channel_message_id:{lottery_id}")
    if result:
        return int(result)
    return result


async def set_channel_message_id(lottery_id: int, message_id: int):
    await redis.set(f"channel_message_id:{lottery_id}", int(message_id))
