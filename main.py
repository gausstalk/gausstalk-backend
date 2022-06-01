'''
gausstalk backend entrypoint
'''

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps import router as apps_router
from services import redis_cache

app = FastAPI()
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


@app.get("/")
def say_hi():
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
