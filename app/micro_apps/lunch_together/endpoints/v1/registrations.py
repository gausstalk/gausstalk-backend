"""
CRUD of Lunch Together registrations.
Path: /apps/lunch-together/v1/registrations/
"""

# pylint: disable=duplicate-code

from typing import List

from bson import ObjectId
from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.micro_apps.lunch_together.models.registration import Registration
from app.micro_apps.user.models.auth import User
from app.micro_apps.user.models.message import Message
from app.micro_apps.user.services.auth_service import auth_user
from app.micro_apps.user.services.user_info import get_name
from app.services.mongo_service import get_mongo

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=List[Registration],
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def get_registrations(
        appointment_id: str,
        database=Depends(get_mongo),
):
    """
    Get registrations.
    """

    try:
        registrations = list(
            database.lunch_registrations.find({
                'appointment_id': ObjectId(appointment_id),
            }))
        if len(registrations) == 0:
            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT
            )

        for register in registrations:
            register['appointment_id'] = str(register['appointment_id'])
            register['participant_name'] = get_name(
                register['participant_mail']
            )
        return registrations
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )


@router.put(
    '/',
    responses={
        status.HTTP_200_OK: {
            'model': Message,
        },
        status.HTTP_201_CREATED: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def put_registration(
        appointment_id: str,
        user: User = Depends(auth_user),
        database=Depends(get_mongo),
):
    """
    Put registration.
    """

    try:
        document = {
            'appointment_id': ObjectId(appointment_id),
            'participant_mail': user['mail'],
        }
        result = database.lunch_registrations.update_one(
            document,
            {'$set': document},
            upsert=True,
        )
        if result.matched_count == 0:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={'message': 'Registration created.'},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Registration exists.'},
        )
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )


@router.delete(
    '/',
    responses={
        status.HTTP_200_OK: {
            'model': Message,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def delete_registration(
        appointment_id: str,
        user: User = Depends(auth_user),
        database=Depends(get_mongo),
):
    """
    Delete registration.
    """

    try:
        result = database.lunch_registrations.delete_one({
            'appointment_id':
            ObjectId(appointment_id),
            'participant_mail':
            user['mail'],
        })
        if result.deleted_count == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={'message': 'Registration not found.'},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Registration deleted.'},
        )
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )
