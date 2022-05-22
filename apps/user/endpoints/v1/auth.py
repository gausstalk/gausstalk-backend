import logging
import os
from datetime import datetime, timedelta

import requests
from fastapi import status, APIRouter, Request, Response
from fastapi.responses import JSONResponse
from jose import jwt

from ...models import auth
from ...models.message import Message

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = 'HS256'

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.get(
    '/',
    response_model=auth.User,
    responses={401: {'model': Message}},
)
def auth_get(gauss_access_token: str | None = None):
    try:
        user_info = jwt.decode(gauss_access_token, SECRET_KEY, ALGORITHM)
        print(user_info)
    # pylint: disable=broad-except
    except Exception as error:
        logging.error(error)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'message': 'gauss_access_token is not valid.'}
        )
    return {'mail': user_info['sub'], 'name': user_info['name']}


@router.post(
    '/',
    response_model=auth.AccessToken,
    responses={500: {"model": Message}},
)
def auth_post(body: auth.Auth, response: Response):
    # get ms_access_token
    ms_response = requests.post(
        'https://login.microsoftonline.com/cfcd9b87-7c5a-4042-9129-abee6253febe/oauth2/v2.0/token',
        data={
            'client_id': '7fc37514-c400-4b28-a6d6-e19a9ae981b6',
            'scope': 'offline_access User.read',
            'code': body.code,
            'redirect_uri': 'http://localhost:3000/auth',
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


@router.delete('/')
def auth_delete(request: Request):
    # delete gauss_refresh_token from DB
    # request.cookies.get('gauss_refresh_token')
    return JSONResponse(status_code=200)
