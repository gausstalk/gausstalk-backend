"""
Get Korean holidays.
Path: /apps/utils/v1/holidays/kr/
"""

from datetime import datetime
from typing import List
import os

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
def get_kr_holidays(year: int, month: int):
    """
    Get holidays of a specific year/month.
    """

    # just params dict not working cuz maybe % str
    # so I chose to pass it as str
    params = '&'.join([
        f'solYear={year}',
        f'solMonth={str(month).zfill(2)}',
        f'ServiceKey={os.environ.get("HOLIDAYS_KR_SERVICE_KEY")}',
        f'numOfRows={100}',
        '_type=json',
    ])

    response = requests.get(
        'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/'
        'getRestDeInfo',
        params=params,
    )

    if response.status_code != 200:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Request to data.go.kr failed.'},
        )

    response_json = response.json()

    if not response_json['response']['body']['items']:
        return []

    holidays = []

    items = response_json['response']['body']['items']['item']
    if not isinstance(items, list):
        items = [items]

    for item in items:
        holidays.append({
            'name':
            item['dateName'],
            'date':
            str(datetime.strptime(str(item['locdate']), '%Y%m%d').date()),
        })
    return holidays
