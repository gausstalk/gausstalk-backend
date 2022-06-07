"""
chat models
"""

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from datetime import datetime

from pydantic import BaseModel


class Chat(BaseModel):
    """
    Chat response
    """
    content: str


class DBChat(BaseModel):
    """
    Chat model that goes in db
    """
    sender: str
    time: datetime
    content: str
