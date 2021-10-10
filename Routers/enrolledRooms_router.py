from fastapi import APIRouter, Depends, Request, HTTPException, status
from Database import database, models
from sqlalchemy.orm import Session
from Functions.Token import getCurrentUser
from pydantic import BaseModel
from typing import  Optional, List
from Functions.EnrolledFunctions import joinRoom, getEnrolledRooms
import time

router = APIRouter(
    tags=['Enrolled Rooms'],
    # prefix="/auth"
)

get_db = database.get_db

class JoinRoomSchema (BaseModel):
    roomId: int


@router.get('/join_room')
def joinRoomRoute(
    roomId: int,
    request: Request,
    db: Session = Depends(get_db),
):
    time.sleep(2)
    print(roomId)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return joinRoom(roomId, tokenData, db)


@router.get('/enrolled_rooms')
def enrolledRooms(
    request: Request,
    db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getEnrolledRooms(tokenData, db)
