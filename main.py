from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import API

API.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

App = FastAPI()
App.mount("/app/gausstalk/v1", API)


def run():
    import uvicorn
    uvicorn.run(App)


# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()
