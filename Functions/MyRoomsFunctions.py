import json
import os
from os import getenv
from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from sqlalchemy.sql import text
from datetime import datetime
import pytz

from Functions.EnrolledFunctions import leaveRoom
from Functions.MemberQuestionsFunctions import deleteSubmittedFile


def createNewRoom(roomName, tokenData, db: Session):
    newRoom = models.Rooms(
        ownerId = tokenData['userId'],
        name = roomName,
        createdAt = datetime.now(pytz.timezone('Asia/Kolkata')),
        specialFields = json.dumps([])
    )

    db.add(newRoom)
    db.commit()
    db.refresh(newRoom)

    myRooms = getMyRooms(tokenData, db)['myRooms']
    return {"newRoomId": newRoom.id, "myRooms": myRooms}


def updateRoomSettings(roomInfo, tokenData, db: Session):
    room = db.query(models.Rooms).filter(models.Rooms.id == roomInfo.roomId).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    room.name = roomInfo.roomName
    room.visibility = roomInfo.visibility
    room.waitingRoomEnabled = roomInfo.waitingRoomEnabled
    room.specialFields = json.dumps(roomInfo.specialFields)

    db.commit()
    db.refresh(room)

    if not roomInfo.waitingRoomEnabled:
        members = db.execute(text(f"""
                    SELECT id FROM RoomMembers 
                    WHERE roomId = {roomInfo.roomId} AND inWaitingRoom = TRUE AND isRejected = FALSE 
                """)).fetchall()


        for member in members:
            db.execute(text(f"""
                        UPDATE RoomMembers
                        SET inWaitingRoom = False
                        WHERE id = {member[0]}
                    """))
            db.commit()


    roomInfo = {
        "roomId": room.id,
        "roomName": room.name,
        "visibility": room.visibility,
        "waitingRoomEnabled": room.waitingRoomEnabled,
        "enrolled": getEnrolledCount(roomInfo.roomId, db),
        "waitingRoomCount": getWaitingRoomCount(roomInfo.roomId, db)
    }
    myRooms = getMyRooms(tokenData, db)['myRooms']

    return {"roomInfo": roomInfo, "myRooms": myRooms}


def getEnrolledCount(roomId, db: Session):
    return db.execute(text(f"""
        SELECT COUNT(*) 
        FROM RoomMembers 
        WHERE roomId = {roomId} AND inWaitingRoom = FALSE AND isRejected = FALSE;
    """)).fetchone()[0]


def getWaitingRoomCount(roomId, db: Session):
    return db.execute(text(f"""
        SELECT COUNT(*) 
        FROM RoomMembers 
        WHERE roomId = {roomId} AND inWaitingRoom = TRUE AND isRejected = FALSE;
    """)).fetchone()[0]


def getMyRooms(tokenData, db: Session):
    sqlData = db.execute(text(f"""
        SELECT R.id, R.name, R.visibility, COUNT(Q.id) AS questionsCount
        FROM Rooms R
        LEFT JOIN Questions Q on R.id = Q.roomId
        WHERE R.ownerId = {tokenData['userId']}
        GROUP BY R.id
    """)).fetchall()

    myRooms = []
    for row in sqlData:
        # print(row)
        myRooms.append({
            "roomId": row[0],
            "roomName": row[1],
            "visibility": row[2],
            "questions": row[3],
            "enrolled": getEnrolledCount(row[0], db),
        })

    return {"myRooms": myRooms}


def getRoomById(roomId, tokenData, db: Session):
    myRoom = db.execute(text(f"""
        SELECT id, ownerId, name, visibility, waitingRoomEnabled, specialFields
        FROM Rooms
        WHERE id = {roomId}
    """)).fetchone()

    if not myRoom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room not found.")

    if tokenData['userId'] != myRoom[1]: #Index 1 is ownerId
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    roomInfo = {
        "roomId": myRoom[0],
        "roomName": myRoom[2],
        "visibility": myRoom[3],
        "waitingRoomEnabled": myRoom[4] == 1,
        "enrolled": getEnrolledCount(roomId, db),
        "waitingRoomCount": getWaitingRoomCount(roomId, db),
        "specialFields": json.loads(myRoom[5])
    }

    questionData = db.execute(text(f"""
        SELECT id, title, isVisible, endTime, _type
        FROM Questions Q 
        WHERE roomId = {roomId}
    """)).fetchall()

    questions = []
    for question in questionData:
        questions.append({
            "questionId": question[0],
            "title": question[1],
            "isVisible": question[2],
            "endTime": question[3],
            "type": question[4],
            "submitted": db.execute(text(f"""
                SELECT COUNT(DISTINCT userId) 
                FROM CodeSubmissions 
                WHERE questionId = {question[0]}
            """)).fetchone()[0]
                         +
                         db.execute(text(f"""
                SELECT COUNT(DISTINCT userId) 
                FROM FileSubmissions 
                WHERE questionId = {question[0]}
            """)).fetchone()[0]
        })

    return {"roomInfo": roomInfo, "questions": questions}


def verifyRoomOwner(roomId, tokenData, db: Session):
    room = db.query(models.Rooms).filter(models.Rooms.id == roomId).first()

    if not room or room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Room.")

    return room


def getRoomMembers(roomId, waiting, db: Session ):

    roomMembers = db.execute(text(f"""
                    SELECT U.id, U.username, U.email, U.fname, U.lname, Rm.id, Rm.specialFields
                    FROM RoomMembers RM
                    LEFT JOIN Users U on U.id = RM.userId
                    WHERE RM.roomId = {roomId} AND RM.isRejected = FALSE AND RM.inWaitingRoom = {waiting}
                    GROUP BY U.id
                """)).fetchall()

    members = []
    for member in roomMembers:
        submitted = 0
        if not waiting:
            questions = db.execute(text(f"""
                                    SELECT id, _type FROM Questions 
                                    WHERE isVisible = TRUE AND roomId = {roomId};
                                """)).fetchall()
            for question in questions:
                if (question[1] == "code"):
                    submitted += min(
                        db.execute(text(f"""
                                    SELECT COUNT(*) FROM CodeSubmissions 
                                    WHERE questionId = {question[0]} AND userId = {member[0]} ;
                                """)).fetchone()[0], 1)
                else:
                    submitted += min(
                        db.execute(text(f"""
                                    SELECT COUNT(*) FROM FileSubmissions 
                                    WHERE questionId = {question[0]} AND userId = {member[0]} ;
                                """)).fetchone()[0], 1)

        members.append({
            "userId": member[0],
            "userName": member[1],
            "email": member[2],
            "name": member[3] + " " + member[4],
            "tableId": member[5],
            "specialFields": json.loads(member[6]),
            "questionsSubmitted": submitted
        })

    return {"members": members}


def modifyRoomMember(roomId, userId, reject, db: Session):
    if reject:
        leaveRoom(roomId, {"userId": userId}, db)
        db.execute(text(f"""
                            DELETE FROM RoomMembers
                            WHERE userId = {userId} AND roomId = {roomId}
                        """))
    else:
        db.execute(text(f"""
                            UPDATE RoomMembers
                            SET isRejected = FALSE, inWaitingRoom = FALSE
                            WHERE userId = {userId} AND roomId = {roomId}
                        """))
    db.commit()
    return True


def deleteRoom(roomId, db):

    questionIds = db.execute(text(f"""
                    SELECT id, _type FROM Questions WHERE roomId={roomId}
                """)).fetchall()

    for id in questionIds:
        if id[1] == "file":
            dir = getenv("BASE_PATH") + f"/SavedFiles/Q_{id[0]}"
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
            os.removedirs(dir)

            db.execute(text(f"""
                    DELETE FROM FileSubmissions 
                    WHERE questionId={id[0]}
            """))
        else:
            db.execute(text(f"""
                DELETE FROM CodeSubmissions
                WHERE questionId = {id[0]}
            """))
            db.execute(text(f"""
                DELETE  FROM SavedCodes
                WHERE questionId = {id[0]}
            """))

    db.execute(text(f"""
        DELETE FROM RoomMembers
        WHERE roomId={roomId}
    """))
    db.execute(text(f"""
        DELETE FROM Questions
        WHERE roomId={roomId}
    """))
    db.execute(text(f"""
        DELETE FROM Rooms
        WHERE id={roomId}
    """))

    db.commit()
    return True
