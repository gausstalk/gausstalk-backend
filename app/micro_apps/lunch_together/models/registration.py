"""
Models for Lunch Together registration.
"""

# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from pydantic import BaseModel


class Registration(BaseModel):
    """
    Registration request body.
    """
    appointment_id: str
    participant_mail: str
    participant_name: str
