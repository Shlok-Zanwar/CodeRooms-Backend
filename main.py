from fastapi import FastAPI, Request, Body, Query
from Database import models, database
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Routers import auth_router, myRooms_router, enrolledRooms_router, questions_router

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

app.include_router(auth_router.router)
app.include_router(enrolledRooms_router.router)
app.include_router(myRooms_router.router)
app.include_router(questions_router.router)


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
