'''
Service module for authentification and authorization.
'''

import logging
import os
from datetime import datetime, timedelta

from fastapi import status, HTTPException, Cookie, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from jose import jwt

from ..models import auth

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = 'HS256'

http_bearer = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    '''
    generate JWT
    '''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode(token):
    '''
    Decode JWT token.
    '''
    try:
        user_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return user_info
    # pylint: disable=broad-except
    except Exception as error:
        raise Exception('Token is not available.') from error


async def auth_user(
    credentials: HTTPBasicCredentials | None = Depends(http_bearer),
    gauss_refresh_token: str | None = Cookie(default=None),
    gauss_access_token: str | None = None,
) -> auth.User | None:
    '''
    Check bearer token and cookie.
    Return User or None.
    '''
    gauss_access_token = credentials.credentials
    try:
        user_info = decode(gauss_access_token)
        return {
            'mail': user_info['sub'],
            'name': user_info['name'],
            'gauss_access_token': gauss_access_token,
        }
    # pylint: disable=broad-except
    except Exception as error:
        logging.debug('Decoding gauss_access_token failed. %s', error)

    try:
        user_info = decode(gauss_refresh_token)
        gauss_access_token = create_access_token(
            data={
                'sub': user_info['sub'],
                'name': user_info['name'],
            },
            expires_delta=timedelta(days=14),
        )
        return {
            'mail': user_info['sub'],
            'name': user_info['name'],
            'gauss_access_token': gauss_access_token,
        }
    # pylint: disable=broad-except
    except Exception as error:
        logging.debug('Regenerating gauss_access_token failed. %s', error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from error
