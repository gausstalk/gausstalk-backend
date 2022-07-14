'''
path functions for authentification and authorization
router prefix is /apps/user/v1/auth
'''

import os
import urllib.parse
from datetime import timedelta

import requests
from fastapi import status, APIRouter, Response, Cookie, Depends
from fastapi.responses import JSONResponse

from app.services.mongo_service import get_mongo
from ...services.auth_service import auth_user, create_token
from ...models import auth
from ...models.message import Message

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = 'HS256'

router = APIRouter()


@router.get(
    '/',
    response_model=auth.User,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': Message},
    },
)
def get_auth(
    response: Response,
    user: auth.User = Depends(auth_user),
    database=Depends(get_mongo),  # MongoDB database
    gauss_refresh_token: str | None = Cookie(default=None),
):
    """ Check if there's already the user in the DB. """
    if database.user.find_one({'mail': user['mail']}):
        if gauss_refresh_token is None:
            gauss_refresh_token = create_token(
                data={'sub': user['mail'], 'name': user['name']},
                expires_delta=timedelta(days=14),
            )
            response.set_cookie('gauss_refresh_token', gauss_refresh_token,
                                secure=True, httponly=True, expires=14*24*60*60)
        return user

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'message': 'User not found.'},
    )


@router.post(
    '/',
    response_model=auth.MsAccessToken,
    responses={500: {'model': Message}},
)
def post_auth(body: auth.Auth):
    '''
    ms login
    '''
    # get ms_access_token
    ms_response = requests.post(
        'https://login.microsoftonline.com/cfcd9b87-7c5a-4042-9129-abee6253febe/oauth2/v2.0/token',
        data={
            'client_id': '7fc37514-c400-4b28-a6d6-e19a9ae981b6',
            'scope': 'offline_access User.read',
            'code': body.code,
            'redirect_uri': urllib.parse.urljoin(os.environ['DOMAIN'], 'auth'),
            'grant_type': 'authorization_code',
            'client_secret': os.environ['CLIENT_SECRET'],
        },
    )
    if ms_response.status_code != status.HTTP_200_OK:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Error to post login.microsoftonline.com'},
        )
    ms_response_json = ms_response.json()
    try:
        ms_access_token = ms_response_json['access_token']
    except KeyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Error to get ms_access_token'},
        )

    return {'ms_access_token': ms_access_token}


@router.delete(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=Message,
    responses={status.HTTP_401_UNAUTHORIZED: {'model': Message}},
)
async def delete_auth(response: Response):
    """
    logout
    """
    response.delete_cookie('gauss_refresh_token')
    return {'message': 'Deleted gauss_refresh_token.'}
