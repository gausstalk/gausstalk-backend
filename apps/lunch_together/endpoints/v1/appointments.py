"""
CRUD of Lunch Together appointments.
Path: /apps/lunch-together/v1/appointments/
"""

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from apps.user.models.auth import User
from apps.user.models.message import Message
from apps.user.services.auth_service import auth_user
from services.mongo_service import get_mongo
from ...models.appointments import Appointment

router = APIRouter()


@router.post(
    '/',
    responses={
        status.HTTP_201_CREATED: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def post_appointment(
        appointment: Appointment,
        database=Depends(get_mongo),
        user: User = Depends(auth_user),
):
    """
    Post an appointment.
    """
    try:
        database.lunch_appointments.insert_one({
            'restaurant_id': appointment.restaurant_id,
            'title': appointment.title,
            'datetime': appointment.datetime,
            'n_participants': appointment.n_participants,
            'meeting_point': appointment.meeting_point,
            'organizer_mail': user['mail'],
        })
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={'message': 'Appointment created.'},
        )
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )


@router.delete(
    '/{appointment_id}',
    dependencies=[Depends(auth_user)],
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
def delete_appointment(
        appointment_id: str,
        database=Depends(get_mongo),
):
    """
    Delete an appointment.
    """
    try:
        result = database.lunch_appointments.delete_one({
            '_id':
            ObjectId(appointment_id),
        })
        if result.deleted_count == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={'message': 'Appointment not found.'},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'Appointment deleted.'},
        )
    except InvalidId as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': str(error)},
        )
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )
