'''
module for redis
'''

import asyncio
import logging
import os

import redis.asyncio as redis
from fastapi import WebSocket

try:
    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = int(os.getenv("REDIS_PORT"))  # might raise TypeError
    redis_db: int = int(os.getenv("REDIS_DB"))      # might raise TypeError
    redis_password: str = os.getenv("REDIS_PASSWORD")
    REDIS = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        socket_timeout=2,
        ssl=True,
    )
    logging.info("Redis connection succeeded.")
except (redis.RedisError, TypeError) as error:
    REDIS = None
    logging.error("Redis connection failed. %s", error)


async def get_redis(websocket: WebSocket):
    '''
    global variable of redis instance
    '''
    return websocket.app.state.redis


async def reader(channel: redis.client.PubSub):
    '''
    read message through redis pub/sub
    '''
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            return message['data'].decode('utf-8')
        await asyncio.sleep(0.01)
