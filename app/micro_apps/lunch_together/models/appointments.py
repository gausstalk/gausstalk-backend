"""
Models for Lunch Together appointments.
"""

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from datetime import datetime

from pydantic import BaseModel


class AppointmentRequest(BaseModel):
    """
    Appointment request body.
    """
    restaurant_id: int | None = None
    title: str
    datetime: datetime
    max_participants: int
    meeting_point: str | None = None


class AppointmentResponse(AppointmentRequest):
    """
    Appointment response body.
    """
    id: str
    organizer_mail: str
    organizer_name: str
