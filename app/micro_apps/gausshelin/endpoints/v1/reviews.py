"""
CRUD of gausshelin reviews.
Path: /apps/gausshelin/v1/reviews
"""

from typing import List
from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from app.micro_apps.user.models.auth import User
from app.micro_apps.user.models.message import Message
from app.micro_apps.user.services.auth_service import auth_user
from app.models.object_id import ObjectIdModel
from app.services.mongo_service import get_mongo
from ...models.reviews import ReviewRequest, ReviewResponse

router = APIRouter()


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'model': ObjectIdModel,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def post_review(
        restaurant_id: int,
        review: ReviewRequest,
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
        object_id = database.gausshelin_reviews.insert_one(review).inserted_id
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'object_id': str(object_id)},
    )


@router.get(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=List[ReviewResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def get_reviews(
        restaurant_id: int,
        database=Depends(get_mongo),
):
    """
    Get reviews of a restaurant from the DB.
    """

    try:
        reviews = list(
            database.gausshelin_reviews.find({
                'restaurant_id': restaurant_id,
            }))
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )

    if len(reviews) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Reviews not found.'},
        )

    # Remove restaurant_id key from review.
    for review in reviews:
        review['id'] = str(review['_id'])
        review.pop('restaurant_id')

    return reviews
