'''
router prefix is /apps/v1/meeting
'''

from fastapi import APIRouter
from .meeting import router as meeting_router
from .email import router as email_router
router = APIRouter()
router.include_router(meeting_router)
router.include_router(email_router, prefix="/email")
