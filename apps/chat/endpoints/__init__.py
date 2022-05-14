from fastapi import APIRouter
from .v1 import Router as v1_router

Router = APIRouter()
Router.include_router(v1_router, prefix='/v1')
