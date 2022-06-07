"""
chat models
"""

from typing import Optional

from pydantic import BaseModel
from datetime import datetime


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
