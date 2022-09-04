"""
Models for /apps/utils/v1/holidays/
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from pydantic import BaseModel


class Holiday(BaseModel):
    """
    Model for a holiday.
    """
    name: str
    date: str
