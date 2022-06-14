'''
Path functions for /apps/meeting
'''

import datetime

from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse

from services.mongo_service import get_mongo
from apps.user.services.auth_service import auth_user

from apps.chat.models.message import Message
from apps.user.models import auth

router = APIRouter()


@router.get(
    '/',
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': Message},
        status.HTTP_404_NOT_FOUND: {'model': Message},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Message}
    },
    dependencies=[Depends(auth_user)],
)
def get_register_exists(
        user: auth.User = Depends(auth_user),
        database=Depends(get_mongo)
):
    """ Check if meeting registration exists """
    today = datetime.date.today()
    if database.meetings.find_one({'mail': user['mail'], 'date': today.strftime("%Y-%m-%d")}):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Register exists'}
        )

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.put(
    '/',
    responses={
        status.HTTP_404_NOT_FOUND: {'model': Message},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': Message}
    },
    dependencies=[Depends(auth_user)],
)
def put_register(
        user: auth.User = Depends(auth_user),
        database=Depends(get_mongo)
):
    """ Add registration to db """
    today = datetime.date.today()

    try:
        database.meetings.insert_one({'mail': user['mail'], 'date': today.strftime("%Y-%m-%d")})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Register completed'}
        )
    except (KeyError, TypeError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
