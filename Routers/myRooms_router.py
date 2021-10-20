from fastapi import APIRouter, Depends, Request, HTTPException, status
from Database import database, models
from sqlalchemy.orm import Session
from Functions.Token import getCurrentUser
from pydantic import BaseModel
from typing import Optional, List
from Functions.MyRoomsFunctions import getMyRooms, createNewRoom, getRoomById, updateRoomById, getRoomMembers, \
    modifyRoomMember, getQuestionSubmission, getSubmittedCode, deleteCurrentRoom
import time

router = APIRouter(
    tags=['My Rooms'],
    # prefix="/auth"
)

get_db = database.get_db


class UpdateRoomInfoSchema(BaseModel):
    roomName: str
    visibility: str
    waitingRoomEnabled: bool
    specialFields: List


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
        print(tokenData)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getMyRooms(tokenData, db)


@router.get('/my_rooms/{roomId}')
def roomById(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
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


@router.get("/question_submissions")
def questionSubmissions(
        questionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getQuestionSubmission(questionId, tokenData, db)

@router.get("/get_submitted_code")
def submittedCodeGet(
        submissionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    # try:
    #     tokenData = getCurrentUser(request.headers['Authorization'])
    # except:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getSubmittedCode(submissionId, db)


@router.get('/room_members/{roomId}')
def roomMembers(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getRoomMembers(roomId, tokenData, False, db)


@router.get('/room_waiting/{roomId}')
def roomMembers(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getRoomMembers(roomId, tokenData, True, db)


@router.get('/remove_room_member')
def removeMember(
        roomId: int,
        userId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return modifyRoomMember(roomId, userId, tokenData, True, db)


@router.get('/accept_room_member')
def acceptMember(
        roomId: int,
        userId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return modifyRoomMember(roomId, userId, tokenData, False, db)

@router.get('/delete_room')
def deleteRoom(
        roomId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return deleteCurrentRoom(roomId,tokenData,db)
