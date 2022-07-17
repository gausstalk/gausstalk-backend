"""
router prefix is /apps/gausshelin/v1
"""

from fastapi import APIRouter
from .reviews import router as reviews_router

router = APIRouter()
router.include_router(reviews_router, prefix='/reviews')
