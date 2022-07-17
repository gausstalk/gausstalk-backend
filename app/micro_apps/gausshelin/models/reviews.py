"""
Model for /apps/gausshelin/v1/reviews.
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from pydantic import BaseModel


class Review(BaseModel):
    """
    Model for gausshelin review.
    """
    stars: int
    comment: str
