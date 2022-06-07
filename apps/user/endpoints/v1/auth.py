'''
path functions for authentification and authorization
router prefix is /apps/user/v1/auth
'''

import os
import urllib.parse
from datetime import timedelta

import requests
from fastapi import status, APIRouter, Response, Depends
from fastapi.responses import JSONResponse

from ...services.auth_service import auth_user, create_access_token
from ...models import auth
from ...models.message import Message

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = 'HS256'

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=auth.User,
    responses={status.HTTP_401_UNAUTHORIZED: {'model': Message}},
)
async def get_auth(user: auth.User | None = Depends(auth_user)):
    '''
    return user if token is valid
    '''
    return user


@router.post(
    '/',
    response_model=auth.AccessToken,
    responses={500: {'model': Message}},
)
def post_auth(body: auth.Auth, response: Response):
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

    # get user info from ms
    ms_response = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + ms_access_token},
    )
    if ms_response.status_code != status.HTTP_200_OK:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Error to get graph.microsoft.com'},
        )
    ms_response_json = ms_response.json()

    # send gauss_access_token, gauss_refresh_token
    gauss_access_token = create_access_token(
        data={
            'sub': ms_response_json['mail'],
            'name': ms_response_json['displayName'],
        },
        expires_delta=timedelta(hours=1),
    )
    gauss_refresh_token = create_access_token(
        data={
            'sub': ms_response_json['mail'],
            'name': ms_response_json['displayName'],
        },
        expires_delta=timedelta(days=14),
    )
    response.set_cookie('gauss_refresh_token', gauss_refresh_token, secure=True, httponly=True)
    return {'gauss_access_token': gauss_access_token}


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
