from fastapi import APIRouter
from .chat import Router as chat_router

Router = APIRouter()
Router.include_router(chat_router, prefix='/chat')
