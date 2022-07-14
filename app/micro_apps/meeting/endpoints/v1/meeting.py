'''
Path functions for /apps/meeting/v1/
'''

import datetime

from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.services.mongo_service import get_mongo
from app.micro_apps.user.services.auth_service import auth_user

from app.micro_apps.chat.models.message import Message
from app.micro_apps.user.models import auth

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
        document = {'mail': user['mail'], 'date': today.strftime("%Y-%m-%d")}
        database.meetings.update_one(
            document,
            {'$set': document},
            upsert=True,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Register completed'}
        )
    except (KeyError, TypeError, PyMongoError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete(
    '/',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        }
    },
)
def delete_register(
        user: auth.User = Depends(auth_user),
        database=Depends(get_mongo),
):
    """ Delete the registration from the DB. """

    today = datetime.date.today()

    try:
        ret = database.meetings.delete_one({
            'mail': user['mail'],
            'date': today.strftime("%Y-%m-%d"),
        })
        if ret.deleted_count == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={'message': 'Registration not found.'},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Deleted registration.'},
        )
    except (KeyError, TypeError, PyMongoError):
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
