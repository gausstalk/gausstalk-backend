from fastapi import APIRouter
from .endpoints import Router as endpoints_router

Router = APIRouter()
Router.include_router(endpoints_router)
