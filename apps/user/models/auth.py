'''
auth models
'''

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from pydantic import BaseModel


class Auth(BaseModel):
    '''
    query params for ms login
    '''
    code: str
    session_state: str


class AccessToken(BaseModel):
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
    gauss_access_token: str | None
