"""
router prefix is /apps/utils/v1
"""

from fastapi import APIRouter
from .holidays_kr import router as holidays_kr_router
from .holidays_us import router as holidays_us_router

router = APIRouter()
router.include_router(holidays_kr_router, prefix='/holidays/kr')
router.include_router(holidays_us_router, prefix='/holidays/us')
