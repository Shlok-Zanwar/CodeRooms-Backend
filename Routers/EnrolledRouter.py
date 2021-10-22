from fastapi import APIRouter, Depends, Request, HTTPException, status
from Database import database, models
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import  Optional, List
import time
from Functions.MiscFunctions import verifyJWTToken
from Functions.EnrolledFunctions import joinRoom, getEnrolledRooms, getEnrolledRoomById, leaveRoom

router = APIRouter(
    tags=['Enrolled Rooms'],
)

get_db = database.get_db


class JoinRoomSchema (BaseModel):
    roomId: int
    specialFields: List

@router.post('/join_room')
def joinRoomRoute(
    schema: JoinRoomSchema,
    request: Request,
    db: Session = Depends(get_db),
):
    tokenData = verifyJWTToken(request)
    return joinRoom(schema.roomId, schema.specialFields, tokenData, db)


class LeaveRoomSchema (BaseModel):
    roomId: int

@router.post('/leave_room')
def leaveRoomRoute(
    schema: LeaveRoomSchema,
    request: Request,
    db: Session = Depends(get_db),
):
    tokenData = verifyJWTToken(request)
    return leaveRoom(schema.roomId, tokenData, db)


@router.get('/enrolled_rooms')
def enrolledRooms(
    request: Request,
    db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getEnrolledRooms(tokenData, db)



@router.get('/enrolled_rooms/{roomId}')
def EnrolledRoomById(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getEnrolledRoomById(roomId, tokenData, db)
