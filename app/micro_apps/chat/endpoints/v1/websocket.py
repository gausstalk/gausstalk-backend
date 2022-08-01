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
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Path
from redis.asyncio import Redis

from app.micro_apps.user.services.auth_service import decode
from app.services.redis_cache import get_redis, reader

router = APIRouter()


@router.websocket('/{gauss_access_token}')
async def websocket_endpoint(
    websocket: WebSocket,
    redis: Redis = Depends(get_redis),
    gauss_access_token: str = Path(default=None),
):
    '''
    websocket connection
    '''
    try:
        user = decode(gauss_access_token)
    # pylint: disable=broad-except
    except Exception:
        return

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
                    message = {
                        "sender_mail": user['sub'],
                        "sender_name": user['name'],
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
