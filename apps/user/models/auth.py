'''
auth models
'''

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from typing import Optional

from pydantic import BaseModel


class Auth(BaseModel):
    '''
    query params for ms login
    '''
    code: str
    session_state: str


class GaussAccessToken(BaseModel):
    '''
    token response
    '''
    gauss_access_token: str | None


class User(BaseModel):
    '''
    user response
    '''
    mail: str
    name: str
    gauss_access_token: Optional[str | None]


class MsAccessToken(BaseModel):
    """
    MS access token.
    """
    ms_access_token: str
