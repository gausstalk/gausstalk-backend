'''
router prefix is /apps
'''

from fastapi import APIRouter
from .chat import router as chat_router
from .user import router as user_router
from .meeting import router as meeting_router

router = APIRouter()
router.include_router(chat_router, prefix='/chat')
router.include_router(user_router, prefix='/user')
router.include_router(meeting_router, prefix="/meeting")
