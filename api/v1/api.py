from fastapi import FastAPI

from .endpoints import websocket

# from ...services.service import init_gausstalk_service

API = FastAPI()
API.include_router(websocket.Router)
