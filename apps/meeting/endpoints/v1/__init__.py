'''
router prefix is /apps/v1/meeting
'''

from fastapi import APIRouter
from services.email import router as email_router
from .meeting import router as meeting_router

router = APIRouter()
router.include_router(meeting_router)
router.include_router(email_router, prefix="/email")
