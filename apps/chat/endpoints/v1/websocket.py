'''
path functions for websocket
router prefix is /apps/apps/v1/ws
'''

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from redis.asyncio import Redis

from services.redis_cache import get_redis, reader

router = APIRouter()


@router.websocket('/')
async def websocket_endpoint(
    websocket: WebSocket,
    redis: Redis = Depends(get_redis),
):
    '''
    websocket connection
    '''
    await websocket.accept()

    channel = redis.pubsub()
    await channel.subscribe('companywide')

    try:
        while True:
            receive_text_coro = websocket.receive_text()
            reader_coro = reader(channel)

            dones, pendings = await asyncio.wait(
                [receive_text_coro, reader_coro],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for pending in pendings:
                pending.cancel()

            for done in dones:
                message = done.result()
                if done.get_coro() == receive_text_coro:
                    await redis.publish('companywide', message)
                elif done.get_coro() == reader_coro:
                    await websocket.send_text(message)
    except WebSocketDisconnect:
        logging.info('Websocket disconnected.')
