"""
Get United States' holidays.
Path: /apps/utils/v1/holidays/us/
"""

from typing import List

from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
import requests

from app.micro_apps.user.models.message import Message
from ...models.holiday import Holiday

router = APIRouter()


@router.get(
    '/',
    response_model=List[Holiday],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': Message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': Message,
        },
    },
)
def get_us_holidays():
    """
    Get holidays of a specific year/month.
    """

    response = requests.get(
        'https://date.nager.at/api/v3/NextPublicHolidays/us',
        verify=False,
    )

    if response.status_code != 200:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Request to date.nager.at failed.'},
        )

    return [
        {'name': holiday['localName'], 'date': holiday['date']}
        for holiday in response.json()
        if holiday['localName'] != 'Good Friday'
    ]
