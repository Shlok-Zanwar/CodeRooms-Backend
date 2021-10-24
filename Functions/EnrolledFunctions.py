import os
from os import getenv
import pytz
from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from sqlalchemy.sql import text
from datetime import datetime
import json


def joinRoom(roomId, specialFields, tokenData, db: Session):
    roomInfo = db.execute(text(f"""
                    SELECT ownerId, waitingRoomEnabled, visibility, name, specialFields
                    FROM Rooms 
                    WHERE id = {roomId}
                """)).fetchone()
    waitingRoomEnabled = roomInfo[1]
    roomName = roomInfo[3]
    specialFieldsDB = json.loads(roomInfo[4])

    if not roomInfo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Room.")

    if roomInfo[0] == tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot join your own room.")

    if roomInfo[2] == "hidden":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Unable to join room.")

    roomMemberInfo = db.execute(text(f"""
        SELECT inWaitingRoom, isRejected 
        FROM RoomMembers 
        WHERE roomId = {roomId} AND userId = {tokenData['userId']};
    """)).fetchone()

    if roomMemberInfo:
        if roomMemberInfo[1]:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Unable to join room.")

        if roomMemberInfo[0]:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You are already in waiting room.")

    if len(specialFieldsDB) != len(specialFields):
        return {"specialFields": specialFieldsDB}

    newMember = models.RoomMembers(
        roomId = roomId,
        userId = tokenData['userId'],
        joinedAt = datetime.now(pytz.timezone('Asia/Kolkata')),
        inWaitingRoom = waitingRoomEnabled,
        isRejected = False,
        specialFields = specialFields
    )

    db.add(newMember)
    db.commit()
    db.refresh(newMember)

    return {
        "enrolledRooms": getEnrolledRooms(tokenData, db)['enrolledRooms'],
        "roomName": roomName,
        "waitingRoomEnabled": waitingRoomEnabled
    }


def getEnrolledRooms(tokenData, db: Session):
    enrolledRooms = db.execute(text(f"""
        SELECT RM.roomId, R.name
        FROM RoomMembers RM
        LEFT JOIN Rooms R on R.id = RM.roomId
        WHERE RM.userId = {tokenData['userId']} AND RM.inWaitingRoom = FALSE AND RM.isRejected = FALSE
        AND R.visibility <> "hidden"
        GROUP BY RM.roomId
    """)).fetchall()

    data = []
    for room in enrolledRooms:
        questions = db.execute(text(f"""
                        SELECT id, _type FROM Questions 
                        WHERE isVisible = TRUE AND roomId = {room[0]};
                    """)).fetchall()

        submitted = 0
        for question in questions:
            if(question[1] == "code"):
                submitted += min(
                    db.execute(text(f"""
                        SELECT COUNT(*) FROM CodeSubmissions 
                        WHERE questionId = {question[0]} AND userId = {tokenData['userId']} ;
                    """)).fetchone()[0], 1)
            else:
                submitted += min(
                    db.execute(text(f"""
                        SELECT COUNT(*) FROM FileSubmissions 
                        WHERE questionId = {question[0]} AND userId = {tokenData['userId']} ;
                    """)).fetchone()[0], 1)


        data.append({
            "roomId": room[0],
            "roomName": room[1],
            "questions": len(questions),
            "submitted": submitted
        })

    return {"enrolledRooms": data}


def getEnrolledRoomById(roomId, tokenData, db: Session):
    roomData = db.execute(text(f"""
                       SELECT id, userId, inWaitingRoom, isRejected 
                       FROM RoomMembers
                       WHERE roomId={roomId} AND userId={tokenData['userId']} AND isRejected = FALSE AND inWaitingRoom = FALSE
                    """)).fetchone()

    if not roomData:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")

    extraInfo = db.execute(text(f"""
                    SELECT R.ownerId, R.name, U.fname,U.lname 
                    FROM Rooms R JOIN Users U on R.ownerId = U.id
                    WHERE R.id = {roomId}
                    GROUP BY R.ownerId
                """)).fetchone()

    roomQuestions = db.execute(text(f"""
           SELECT id, title, endTime, _type
           FROM Questions Q 
           WHERE roomId = {roomId} AND isVisible = TRUE
       """)).fetchall()

    questions = []
    for row in roomQuestions:
        if row[3] == "code":
            submissionTime = db.execute(text(f"""
                                SELECT submittedAt from CodeSubmissions 
                                WHERE userId = {tokenData['userId']} AND questionId = {row[0]}
                            """)).fetchone()
        else:
            submissionTime = db.execute(text(f"""
                                SELECT submittedAt from FileSubmissions 
                                WHERE userId = {tokenData['userId']} AND questionId = {row[0]}
                            """)).fetchone()

        questions.append({
            "questionId": row[0],
            "title": row[1],
            "endTime": row[2],
            "_type": row[3],
            "isSubmitted": False if not submissionTime else True,
            "submissionTime": None if not submissionTime else submissionTime[0]
        })

    roomInfo = {
        "roomId": roomId,
        "host": extraInfo[2] + " " + extraInfo[3],
        "roomName": extraInfo[1]
    }

    return {"roomInfo": roomInfo, "questions": questions}


def leaveRoom(roomId, tokenData, db: Session):
    questions = db.execute(text(f"""
                    SELECT id, _type FROM Questions 
                    WHERE roomId={roomId}
                """)).fetchall()

    for question in questions:

        if question[1] == "code":
            db.execute(text(f"""
                DELETE FROM CodeSubmissions
                WHERE questionId={question[0]} AND userId={tokenData['userId']}
            """))
            db.execute(text(f"""
                DELETE FROM SavedCodes
                WHERE questionId={question[0]} AND userId={tokenData['userId']}
            """))
        else:
            sub = db.execute(text(f"""
                SELECT id FROM FileSubmissions
                WHERE questionId={question[0]} AND userId={tokenData['userId']}
            """)).fetchone()

            if sub:
                os.remove(getenv("BASE_PATH") + f"/SavedFiles/Q_{question[0]}/SID_{sub[0]}.pdf")
                db.execute(text(f"""
                                DELETE FROM FileSubmissions
                                WHERE id={sub[0]}
                            """))

    db.execute(text(f"""
        DELETE FROM RoomMembers
        WHERE roomId={roomId} AND userId={tokenData['userId']}
    """))

    db.commit()

    return True

