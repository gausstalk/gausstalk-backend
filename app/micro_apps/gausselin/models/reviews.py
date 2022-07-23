"""
Model for /apps/gausselin/v1/reviews.
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from typing import Optional

from pydantic import BaseModel, constr


class ReviewRequest(BaseModel):
    """
    Model for gausselin review request.
    """
    restaurant_id: int
    restaurant_name: str | None
    stars: int
    comment: constr(max_length=280) | None


class ReviewResponse(ReviewRequest):
    """
    Model for gausselin review response.
    """
    id: str
    user_mail: str
    user_name: Optional[str]
