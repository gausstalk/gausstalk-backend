"""
CRUD of Lunch Together registrations.
Path: /apps/lunch-together/v1/registrations/
"""

from datetime import datetime

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt

from app.micro_apps.user.services.auth_service import SECRET_KEY, ALGORITHM, auth_user
from app.main import app
from app.services.mongo_service import get_mongo

client = TestClient(app)


async def fake_auth_user():
    """
    Dependency injection on behalf of Depends(auth_user).
    """

    mail = 'yonsweng@gmail.com'
    name = 'Choi Yeonung'
    to_encode = {'sub': mail, 'name': name}
    return {
        'mail': mail,
        'name': name,
        'gauss_access_token': jwt.encode(to_encode, SECRET_KEY, ALGORITHM),
    }


app.dependency_overrides[auth_user] = fake_auth_user


def test_registrations(database=get_mongo()):
    """
    Test /apps/lunch-together/v1/registrations/ API.
    """

    # Create an appointment.
    response = client.post(
        '/apps/lunch-together/v1/appointments/',
        json={
            'restaurant_id': 9999999,
            'title': '맛집',
            'datetime': str(datetime.now().isoformat()),
            'n_participants': 5,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    appointment_id = response.json()['object_id']

    # Create an registration for the appointment.
    response = client.put(
        '/apps/lunch-together/v1/registrations/',
        params={'appointment_id': appointment_id},
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Get the registration.
    response = client.get(
        '/apps/lunch-together/v1/registrations/',
        params={'appointment_id': appointment_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    # Delete the registration.
    response = client.delete(
        '/apps/lunch-together/v1/registrations/',
        params={'appointment_id': appointment_id},
    )
    assert response.status_code == status.HTTP_200_OK

    # Check if the registration is deleted.
    response = client.get(
        '/apps/lunch-together/v1/registrations/',
        params={'appointment_id': appointment_id},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Delete the appointment.
    result = database.lunch_appointments.delete_one({
        '_id':
        ObjectId(appointment_id),
    })
    assert result.deleted_count == 1
