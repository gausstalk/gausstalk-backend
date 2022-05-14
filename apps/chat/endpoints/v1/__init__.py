from fastapi import APIRouter
from .websocket import Router as websocket_router

Router = APIRouter()
Router.include_router(websocket_router)
