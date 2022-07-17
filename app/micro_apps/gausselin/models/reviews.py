"""
Model for /apps/gausselin/v1/reviews.
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from pydantic import BaseModel


class Review(BaseModel):
    """
    Model for gausselin review.
    """
    stars: int
    comment: str
