"""
Path functions for /apps/user/v1/user
"""

from datetime import timedelta

from fastapi import status, APIRouter, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials

from services.mongo_service import get_mongo
from ...services.auth_service import create_token, get_user_from_ms, http_bearer
from ...models import auth
from ...models.message import Message

router = APIRouter()


@router.get(
    '/',
    response_model=auth.User,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': Message},
    },
)
def get_user(
    response: Response,
    credentials: HTTPBasicCredentials | None = Depends(http_bearer),
    database=Depends(get_mongo),  # MongoDB database
):
    """ Check if there's already the user in the DB. """
    ms_access_token = credentials.credentials

    user = get_user_from_ms(ms_access_token)
    if user:
        mail, name = user['mail'], user['name']

        if database.user.find_one({'mail': mail, 'name': name}):
            gauss_access_token = create_token(
                data={'sub': mail, 'name': name},
                expires_delta=timedelta(minutes=15),
            )
            gauss_refresh_token = create_token(
                data={'sub': mail, 'name': name},
                expires_delta=timedelta(days=14),
            )
            response.set_cookie('gauss_refresh_token', gauss_refresh_token,
                                secure=True, httponly=True, expires=14*24*60*60)
            return {
                'mail': mail,
                'name': name,
                'gauss_access_token': gauss_access_token,
            }

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'message': 'User not found.'},
    )


@router.put(
    '/',
    response_model=auth.User,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': Message},
        status.HTTP_409_CONFLICT: {'model': Message},
    },
)
def put_user(
    body: auth.MsAccessToken,
    response: Response,
    database=Depends(get_mongo),  # MongoDB database
):
    """ Create a user if not existing. """
    user = get_user_from_ms(body.ms_access_token)
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'message': 'ms_access_token is not valid.'}
        )

    mail, name = user['mail'], user['name']

    # Check if there's already the same user.
    if database.user.find_one({'mail': mail}):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={'message': 'The user already exists.'},
        )

    database.user.insert_one({
        'mail': mail,
        'name': name,
    })

    gauss_access_token = create_token(
        data={'sub': mail, 'name': name},
        expires_delta=timedelta(minutes=15),
    )
    gauss_refresh_token = create_token(
        data={'sub': mail, 'name': name},
        expires_delta=timedelta(days=14),
    )
    response.set_cookie('gauss_refresh_token', gauss_refresh_token,
                        secure=True, httponly=True, expires=14*24*60*60)
    return {
        'mail': mail,
        'name': name,
        'gauss_access_token': gauss_access_token,
    }
