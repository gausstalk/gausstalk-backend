"""
CRUD of gausselin reviews.
Path: /apps/gausselin/v1/reviews
"""

from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from app.micro_apps.user.models.auth import User
from app.micro_apps.user.models.message import Message
from app.micro_apps.user.services.auth_service import auth_user
from app.models.object_id import ObjectIdModel
from app.services.mongo_service import get_mongo
from ...models.reviews import Review

router = APIRouter()


@router.post(
    '/',
    response_model=ObjectIdModel,
    responses={
        status.HTTP_201_CREATED: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def post_review(
        restaurant_id: int,
        review: Review,
        user: User = Depends(auth_user),
        database=Depends(get_mongo),
):
    """
    Post a review into the DB.
    """

    try:
        review = review.dict()
        review['restaurant_id'] = restaurant_id
        review['user_mail'] = user['mail']
        object_id = database.gausselin_reviews.insert_one(review).inserted_id
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'object_id': str(object_id)},
    )
