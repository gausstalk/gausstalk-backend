"""
Model for MongoDB ObjectId
"""

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from pydantic import BaseModel


class ObjectIdModel(BaseModel):
    """
    Model for MongoDB ObjectId
    """
    object_id: str
