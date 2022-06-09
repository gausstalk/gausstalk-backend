'''
path functions for websocket
router prefix is /apps/apps/v1/ws
'''

import asyncio
import json
import logging
from datetime import datetime

import pytz
from bson import json_util
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from redis.asyncio import Redis

from services.redis_cache import get_redis, reader

router = APIRouter()


def clean_message(message):
    """clean_message"""
    def escape(htmlstring):
        """Clean up html from the incoming string"""
        escapes = {'"': "&quot;", "'": "&#39;", "<": "&lt;", ">": "&gt;"}
        # This is done first to prevent escaping other escapes.
        htmlstring = htmlstring.replace("&", "&amp;")
        for seq, esc in escapes.items():
            htmlstring = htmlstring.replace(seq, esc)
        return htmlstring

    return escape(message)


@router.websocket('/')
async def websocket_endpoint(
    websocket: WebSocket,
    redis: Redis = Depends(get_redis)
):
    '''
    websocket connection
    '''
    await websocket.accept()
    channel = redis.pubsub()
    await channel.subscribe('companywide')

    try:
        while True:
            client_to_redis = websocket.receive_text()
            redis_to_client = reader(channel)

            dones, pendings = await asyncio.wait(
                [client_to_redis, redis_to_client],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for pending in pendings:
                pending.cancel()

            for done in dones:
                if done.get_coro() == client_to_redis:
                    message_text = done.result()
                    message_text = clean_message(message_text)
                    message = {
                        "sender": "Yooha Bae",
                        "time": str(datetime.now(tz=pytz.utc).isoformat()),
                        "content": message_text
                    }
                    message_json = json.dumps(message, default=json_util.default)
                    await redis.publish('companywide', message_json)
                    await redis.lpush("companywide", message_json)
                elif done.get_coro() == redis_to_client:
                    message_json = done.result()
                    await websocket.send_json(message_json)
    except WebSocketDisconnect:
        logging.info('Websocket disconnected.')
