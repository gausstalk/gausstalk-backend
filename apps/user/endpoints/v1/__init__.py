'''
router prefix is /apps/user/v1
'''

from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router

router = APIRouter()
router.include_router(auth_router, prefix='/auth')
router.include_router(user_router, prefix='/user')
