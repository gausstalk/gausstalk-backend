'''
message models
'''

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from pydantic import BaseModel


class Message(BaseModel):
    '''
    error message or something
    '''
    message: str
