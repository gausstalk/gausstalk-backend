'''
gausstalk backend entrypoint
'''

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.micro_apps import router as apps_router
from app.services.email import send_emails_daily
from app.services import redis_cache, mongo_service

app = FastAPI()
app.router.redirect_slashes = False
app.include_router(apps_router, prefix="/apps")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://talk.gausslabs.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def startup_event():
    '''
    define global variables or other starting statements
    '''
    app.state.redis = redis_cache.REDIS
    app.state.mongo_db = mongo_service.mongo_db

    asyncio.create_task(send_emails_daily())


@app.get("/")
async def say_hi():
    '''
    health check of the server
    '''
    return JSONResponse({'message': 'Hi'})


def run():
    '''
    python main.py로 실행할경우 수행되는 구문
    '''
    uvicorn.run(app)


# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()
