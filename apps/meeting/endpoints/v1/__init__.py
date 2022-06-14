'''
router prefix is /apps/v1/meeting
'''

from fastapi import APIRouter
from .meeting import router as meeting_router
router = APIRouter()
router.include_router(meeting_router)
