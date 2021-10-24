from fastapi import FastAPI, Request, Body, Query
from Database import models, database
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Routers import AuthRouter, EnrolledRouter, MemberQuestionsRouter, MyQuestionsRouter, MyRoomsRouter

app = FastAPI()
models.Base.metadata.create_all(database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(AuthRouter.router)
app.include_router(EnrolledRouter.router)
app.include_router(MemberQuestionsRouter.router)
app.include_router(MyRoomsRouter.router)
app.include_router(MyQuestionsRouter.router)

if __name__ == '__main__':
    from os import mkdir, listdir, getenv
    if 'SavedFiles' not in listdir(getenv("BASE_PATH")):
        data_path = getenv("BASE_PATH") + '/SavedFiles'
        mkdir(data_path)
        mkdir(data_path + '/db')

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
