from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps import Router as apps_router

App = FastAPI()
App.include_router(apps_router, prefix='/apps')
App.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run():
    import uvicorn
    uvicorn.run(App)


# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()
