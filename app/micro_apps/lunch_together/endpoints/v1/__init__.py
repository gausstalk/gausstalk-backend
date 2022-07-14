'''
router prefix is /apps/lunch-together/v1
'''

from fastapi import APIRouter
from .appointments import router as appointments_router
from .registrations import router as registrations_router

router = APIRouter()
router.include_router(appointments_router, prefix='/appointments')
router.include_router(registrations_router, prefix='/registrations')
