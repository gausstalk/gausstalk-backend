import os
import requests
from fastapi import APIRouter

from ...models import auth

router = APIRouter()


@router.post('/')
def auth_post(body: auth.Auth):
    response = requests.post(
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

    response_json = response.json()
    access_token = response_json['access_token']

    response = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + access_token},
    )

    return 'Welcome, ' + response.json()['displayName'] + '!'
