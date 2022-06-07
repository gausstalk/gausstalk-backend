'''
module for redis
'''

import asyncio
import logging
import os
import json

import redis.asyncio as redis
from fastapi import WebSocket
from fastapi import Request

try:
    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = int(os.getenv("REDIS_PORT"))  # might raise TypeError
    redis_db: int = int(os.getenv("REDIS_DB"))  # might raise TypeError
    redis_password: str = os.getenv("REDIS_PASSWORD")
    REDIS = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        socket_timeout=100,
        ssl=True,
    )
    logging.info("Redis connection succeeded.")
except (redis.RedisError, TypeError) as error:
    REDIS = None
    logging.error("Redis connection failed. %s", error)


async def get_redis(request: Request = None, websocket: WebSocket = None):
    """
    global variable of redis instance
    """
    if request:
        return request.app.state.redis
    return websocket.app.state.redis

async def reader(channel: redis.client.PubSub):
    """
    read message through redis pub/sub
    """
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            return message['data'].decode('utf-8')
        await asyncio.sleep(0.01)


async def get_messages(redis, room_name, offset=0, size=30):
    """
    Check if room with such name exists, fetch messages from offset to size
    :param database: redis database
    :param room_name: room name to get the messages from
    :param offset: index of message to retrieve from
    :param size: number of messages to retrieve
    :return: return lists of messages
    """
    room_exists = await redis.exists(room_name)
    if room_exists == 0:
        return []

    values = await redis.lrange(room_name, offset, offset + size)
    values = list(map(lambda x: json.loads(x.decode("utf-8")), values))
    values.reverse()
    return values
