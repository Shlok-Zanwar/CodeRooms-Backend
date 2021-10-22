from fastapi import APIRouter, Depends, Request
from Database import database
from sqlalchemy.orm import Session
from Functions.MiscFunctions import verifyJWTToken
from pydantic import BaseModel
from typing import List
from Functions.MyRoomsFunctions import createNewRoom, updateRoomSettings, getMyRooms, getRoomById, getRoomMembers, verifyRoomOwner, modifyRoomMember, deleteRoom


router = APIRouter(
    tags=['My Rooms'],
)

get_db = database.get_db


class createRoomSchema(BaseModel):
    roomName: str

@router.post('/create_room')
def CreateNewRoomRoute(
        roomInfo: createRoomSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return createNewRoom(roomInfo.roomName, tokenData, db)


class UpdateRoomInfoSchema(BaseModel):
    roomId: int
    roomName: str
    visibility: str
    # visibility: Literal["public", "private", "hidden"]
    waitingRoomEnabled: bool
    specialFields: List

@router.post('/update_room_settings')
def updateRoomSettingsRoute(
        request: Request,
        roomInfo: UpdateRoomInfoSchema,
        db: Session = Depends(get_db),
):
    tokenData = verifyJWTToken(request)
    return updateRoomSettings(roomInfo, tokenData, db)


@router.get('/my_rooms')
def myRoomsRoute(
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getMyRooms(tokenData, db)


@router.get('/my_rooms/{roomId}')
def roomByIdRoute(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getRoomById(roomId, tokenData, db)


@router.get('/room_enrolled_members/{roomId}')
def enrolledMembersRoute(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    verifyRoomOwner(roomId, tokenData, db)
    return getRoomMembers(roomId=roomId, waiting=False, db=db)


@router.get('/room_waiting_members/{roomId}')
def waitingMembersRoute(
        roomId,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    verifyRoomOwner(roomId, tokenData, db)
    return getRoomMembers(roomId=roomId, waiting=True, db=db)



class ModifyRoomMemberSchema(BaseModel):
    roomId: int
    userId: int

@router.post('/accept_room_member')
def acceptMembersRoute(
        schema: ModifyRoomMemberSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    verifyRoomOwner(schema.roomId, tokenData, db)
    return modifyRoomMember(roomId=schema.roomId, userId=schema.userId, reject=False, db=db)


@router.post('/reject_room_member')
def rejectMembersRoute(
        schema: ModifyRoomMemberSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    verifyRoomOwner(schema.roomId, tokenData, db)
    return modifyRoomMember(roomId=schema.roomId, userId=schema.userId, reject=True, db=db)


class DeleteRoomSchema(BaseModel):
    roomId: int

@router.post('/delete_room')
def deleteRoomRoute(
        schema: DeleteRoomSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    verifyRoomOwner(schema.roomId, tokenData, db)
    return deleteRoom(schema.roomId, db)