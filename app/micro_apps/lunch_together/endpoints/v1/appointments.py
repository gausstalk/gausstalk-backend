"""
CRUD of Lunch Together appointments.
Path: /apps/lunch-together/v1/appointments/
"""

from datetime import datetime
from typing import List

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.micro_apps.user.models.auth import User
from app.micro_apps.user.models.message import Message
from app.micro_apps.user.services.auth_service import auth_user
from app.models.object_id import ObjectIdModel
from app.services.mongo_service import get_mongo
from ...models.appointments import AppointmentRequest, AppointmentResponse

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(auth_user)],
    response_model=List[AppointmentResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def get_appointment(offset: int, limit: int, database=Depends(get_mongo)):
    """
    Get an appointment whose datetime is after now.
    """
    try:
        appointments = list(
            database.lunch_appointments.find({
                'datetime': {
                    '$gt': datetime.now(),
                },
            }).sort("datetime", pymongo.ASCENDING).limit(limit).skip(offset))

        # Join lunch_appointments and user collection.
        for appointment in appointments:
            user = database.user.find_one({
                'mail':
                appointment['organizer_mail'],
            })
            appointment['id'] = str(appointment['_id'])
            appointment['organizer_name'] = user['name']

        return appointments
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )


@router.post(
    '/',
    responses={
        status.HTTP_201_CREATED: {
            'model': ObjectIdModel,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def post_appointment(
        appointment: AppointmentRequest,
        database=Depends(get_mongo),
        user: User = Depends(auth_user),
):
    """
    Post an appointment.
    """
    try:
        result = database.lunch_appointments.insert_one({
            'restaurant_id':
            appointment.restaurant_id,
            'title':
            appointment.title,
            'datetime':
            appointment.datetime,
            'n_participants':
            appointment.n_participants,
            'meeting_point':
            appointment.meeting_point,
            'organizer_mail':
            user['mail'],
        })
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={'object_id': str(result.inserted_id)},
        )
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )


@router.put(
    '/{appointment_id}',
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
def put_appointment(
        appointment_id: str,
        appointment: AppointmentRequest,
        database=Depends(get_mongo),
        user: User = Depends(auth_user),
):
    """
    Put an appointment.
    """

    document_dict = {
        'restaurant_id': appointment.restaurant_id,
        'title': appointment.title,
        'datetime': appointment.datetime,
        'n_participants': appointment.n_participants,
        'meeting_point': appointment.meeting_point,
        'organizer_mail': user['mail'],
    }

    try:
        original_appointment = database.lunch_appointments.find_one_and_update(
            {'_id': ObjectId(appointment_id)},
            {'$set': document_dict},
        )
        if original_appointment is not None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={'message': 'Appointment edited.'},
            )
    except PyMongoError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(error)},
        )

    # Create an appointment if not existing.
    document_dict.update({'_id': ObjectId(appointment_id)})
    try:
        database.lunch_appointments.insert_one(document_dict)
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
