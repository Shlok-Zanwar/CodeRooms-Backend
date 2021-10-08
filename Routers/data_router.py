from fastapi import APIRouter, Depends, Request, HTTPException, status
from Database import database, models
from sqlalchemy.orm import Session
from Functions.Token import getCurrentUser
from pydantic import BaseModel
from typing import  Optional, List
from Functions.DataFunctions import getMyRooms, createNewRoom, getRoomById, updateRoomById
import time

router = APIRouter(
    tags=['Data'],
    # prefix="/auth"
)

get_db = database.get_db


class UpdateRoomInfoSchema (BaseModel):
    roomName: str
    visibility: str
    waitingRoomEnabled: bool


@router.get('/create_room')
def createRoom(
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return createNewRoom(tokenData, db)


@router.get('/my_rooms')
def myRooms(
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getMyRooms(tokenData, db)


@router.get('/my_rooms/{roomId}')
def roomById(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getRoomById(roomId, tokenData, db)


@router.post('/update_room/{roomId}')
def updateRoomData(
    request: Request,
    roomId,
    roomData: UpdateRoomInfoSchema,
    db: Session = Depends(get_db),
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return updateRoomById(roomId, roomData, tokenData, db)

