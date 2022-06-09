'''
Path functions for /apps/user/v1/user
'''
from typing import List

from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from ...models.chat import Chat, DBChat
from ...models.message import Message
from services.redis_cache import get_messages, get_redis
from apps.user.services.auth_service import auth_user

router = APIRouter()


@router.get(
    '/',
    response_model=List[DBChat],
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': Message},
        status.HTTP_404_NOT_FOUND: {'model': Message},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Message}
    },
    dependencies=[Depends(auth_user)],
)
async def get_messages_for_selected_room(
        room_name: str,
        offset: int = 0,
        size: int = 30,
        redis: Redis = Depends(get_redis)
):
    """ Get size number of chats """
    try:
        messages = await get_messages(redis, room_name, offset, size)
    # pylint: disable=bare-except
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Error in retrieving messages'},
        )
    return messages
