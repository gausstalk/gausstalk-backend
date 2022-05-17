import os
from datetime import datetime, timedelta

import requests
from fastapi import APIRouter, HTTPException, Response, status
from jose import jwt

from ...models import auth

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


@router.post('/', response_model=auth.AccessToken)
def auth_post(body: auth.Auth, response: Response):
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

    ms_response_json = ms_response.json()
    access_token = ms_response_json['access_token']

    ms_response = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + access_token},
    )

    if ms_response.status_code == status.HTTP_200_OK:
        ms_response_json = ms_response.json()
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
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 'Error to get graph.microsoft.com')
