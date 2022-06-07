'''
router prefix is /apps/apps/v1
'''

from fastapi import APIRouter
from .websocket import router as websocket_router
from .chat import router as chat_router
router = APIRouter()
router.include_router(websocket_router, prefix='/ws')
router.include_router(chat_router)
