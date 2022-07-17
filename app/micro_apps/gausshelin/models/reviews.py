"""
Model for /apps/gausshelin/v1/reviews.
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """
    Model for gausshelin review request.
    """
    stars: int
    comment: str


class ReviewResponse(ReviewRequest):
    """
    Model for gausshelin review response.
    """
    id: str
    user_mail: str
