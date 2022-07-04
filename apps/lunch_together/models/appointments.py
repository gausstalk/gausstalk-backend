"""
Models for Lunch Together appointments.
"""

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from datetime import datetime

from pydantic import BaseModel


class Appointment(BaseModel):
    """
    Appointment model.
    """
    restaurant_id: int | None = None
    title: str
    datetime: datetime
    n_participants: int
    meeting_point: str | None = None
