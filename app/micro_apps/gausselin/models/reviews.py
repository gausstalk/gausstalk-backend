"""
Model for /apps/gausselin/v1/reviews.
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """
    Model for gausselin review request.
    """
    stars: int
    comment: str


class ReviewResponse(ReviewRequest):
    """
    Model for gausselin review response.
    """
    id: str
    user_mail: str
