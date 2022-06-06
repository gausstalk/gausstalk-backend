'''
Path functions for /apps/user/v1/user
'''

from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse

from services.mongo_service import get_mongo
from ...services.auth_service import auth_user
from ...models import auth
from ...models.message import Message

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=Message,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': Message},
        status.HTTP_404_NOT_FOUND: {'model': Message},
    },
)
def get_user(
    mail: str | None = None,
    database = Depends(get_mongo),  # MongoDB database
):
    ''' Check if there's already the user in the DB. '''

    # Check if there's already the same user.
    if database.user.find_one({'mail': mail}):
        return {'message': 'User found.'}

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'message': 'User not found.'},
    )


@router.post(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=Message,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': Message},
        status.HTTP_409_CONFLICT: {'model': Message},
    },
)
def post_user(
    body: auth.User,
    database = Depends(get_mongo),  # MongoDB database
):
    ''' Create a user if not existing. '''

    # Check if there's already the same user.
    if database.user.find_one({'mail': body.mail}):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={'message': 'The user already exists.'},
        )

    database.user.insert_one({
        'mail': body.mail,
        'name': body.name,
    })
    return {'message': 'User created.'}
