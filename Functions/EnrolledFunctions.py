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
        WHERE id = {roomId} AND isDeleted = FALSE
    """))

    roomData = roomInfo.fetchall()
    if len(roomData) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Room.")

    waitingRoomEnabled = roomData[0][1]
    roomName = roomData[0][3]
    specialFieldsDB = json.loads(roomData[0][4])
    if roomData[0][0] == tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot join your own room.")

    if roomData[0][2] == "hidden":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Unable to join room.")

    data = db.execute(text(f"""
        SELECT inWaitingRoom, isRejected 
        FROM RoomMembers 
        WHERE roomId = {roomId} AND userId = {tokenData['userId']};
    """))
    userData = data.fetchall()

    if len(userData) != 0:
        if userData[0][0]:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"You are already in waiting room ..")

        if userData[0][1]:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Unable to join room.")

    if len(specialFieldsDB) != len(specialFields):
        return {"specialFields": specialFieldsDB}

    newMember = models.RoomMembers(
        roomId=roomId,
        userId=tokenData['userId'],
        joinedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
        inWaitingRoom=waitingRoomEnabled,
        isRejected=False,
        specialFields=specialFields
    )

    db.add(newMember)
    db.commit()
    db.refresh(newMember)
    return {"enrolledRooms": getEnrolledRooms(tokenData, db)['enrolledRooms'], "roomName": roomName,
            "waitingRoomEnabled": waitingRoomEnabled}


def getEnrolledRooms(tokenData, db: Session):
    enrolledRooms = db.execute(text(f"""
        SELECT RM.roomId, R.name
        FROM RoomMembers RM
        LEFT JOIN Rooms R on R.id = RM.roomId
        WHERE RM.userId = {tokenData['userId']} AND RM.inWaitingRoom = FALSE AND RM.isRejected = FALSE
        AND R.visibility <> "hidden" AND R.isDeleted = FALSE
        GROUP BY RM.roomId
    """))

    roomData = enrolledRooms.fetchall()
    data = []
    for room in roomData:
        sqlQuestions = db.execute(text(f"""
                        SELECT id FROM Questions 
                        WHERE isVisible = TRUE AND isDeleted = FALSE AND roomId = {room[0]};
                    """))
        questions = sqlQuestions.fetchall()
        submitted = 0
        for question in questions:
            submitted += min(
                db.execute(text(f"""
                    SELECT COUNT(*) FROM Submissions 
                    WHERE questionId = {question[0]} AND userId = {tokenData['userId']} AND isDeleted = FALSE ;
                """)).fetchone()[0], 1)

        data.append({
            "roomId": room[0],
            "roomName": room[1],
            "questions": len(questions),
            "submitted": submitted
        })

    return {"enrolledRooms": data}


def getEnrolledRoomById(roomId, tokenData, db: Session):
    enrolledRoom = db.execute(text(f"""
                       SELECT id, userId, inWaitingRoom, isRejected 
                       FROM RoomMembers
                       WHERE roomId={roomId} AND userId={tokenData['userId']} AND isRejected=FALSE AND inWaitingRoom=FALSE
                    """))

    roomData = enrolledRoom.fetchone()

    if not roomData:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")

    extraInfo = db.execute(text(f"""
        SELECT R.ownerId, R.name, U.fname,U.lname 
        FROM Rooms R JOIN Users U on R.ownerId = U.id
        GROUP BY R.ownerId
        """)).fetchone()

    roomQuestions = db.execute(text(f"""
           SELECT id, title, endTime
           FROM Questions Q 
           WHERE roomId = {roomId} AND isDeleted = FALSE  AND isVisible=TRUE
       """)).fetchall()

    questions = []
    for row in roomQuestions:
        questions.append({
            "questionId": row[0],
            "title": row[1],
            "endTime": row[2],
            "isSubmitted": db.execute(text(f"""
                                SELECT COUNT(*) from Submissions 
                                WHERE userId = {tokenData['userId']} AND questionId = {row[0]} AND isDeleted = FALSE
                            """)).fetchone()[0] > 0
        })

    roomInfo = {
        "id": roomId,
        "host": extraInfo[2] + " " + extraInfo[3],
        "roomName": extraInfo[1]
    }

    return {"roomInfo": roomInfo, "questions": questions}
