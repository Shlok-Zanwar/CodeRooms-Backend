from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from Functions.Token import getCurrentUser
from sqlalchemy.sql import text
from datetime import datetime
import random

def getEnrolledCount(roomId, db: Session):
    return db.execute(text(f"""
        SELECT COUNT(*) 
        FROM RoomMembers 
        WHERE roomId = {roomId} AND inWaitingRoom = FALSE AND isRejected = FALSE;
    """)).fetchone()[0]

def createNewRoom(tokenData, db: Session):
    newRoom = models.Rooms(
        ownerId = tokenData['userId'],
        name = "New Room" + str(random.randint(1, 100)),
        createdAt = datetime.now()
    )

    db.add(newRoom)
    db.commit()
    db.refresh(newRoom)

    myRooms = getMyRooms(tokenData, db)['myRooms']
    # print(newRoom)
    return {"newRoomId": newRoom.id, "myRooms": myRooms}


def getMyRooms(tokenData, db: Session):
    myRooms = db.execute(text(f"""
        SELECT R.id, R.name, R.visibility, COUNT(Q.id) AS questionsCount 
        FROM Rooms R
        LEFT JOIN Questions Q on R.id = Q.roomId
        WHERE R.ownerId = {tokenData['userId']} AND R.isDeleted = FALSE
        GROUP BY R.id
    """))

    sqlData = myRooms.fetchall()
    data = []
    for row in sqlData:
        # print(row)
        data.append({
            "roomId": row[0],
            "roomName": row[1],
            "visibility": row[2],
            "questions": row[3],
            "enrolled": getEnrolledCount(row[0], db),
        })

    return {"myRooms": data}


def getRoomById(roomId, tokenData, db: Session):
    myRoom = db.execute(text(f"""
        SELECT id, ownerId, name, visibility, waitingRoomEnabled FROM Rooms
        WHERE id = {roomId} AND isDeleted = FALSE
    """))

    sqlData = myRoom.fetchone()

    if not sqlData:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room not found.")

    if tokenData['userId'] != sqlData[1]: #Index 1 is ownerId
        print(tokenData['userId'])

        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    roomInfo = {
        "roomId": sqlData[0],
        "roomName": sqlData[2],
        "visibility": sqlData[3],
        "waitingRoomEnabled": sqlData[4] == 1,
        "enrolled": getEnrolledCount(roomId, db),
    }

    # print(sqlData)
    # roomQuestions = db.execute(text(f"""
    #         SELECT Q.id, Q.title, Q.isVisible, COUNT(DISTINCT S.userId)
    #         FROM Questions Q
    #         LEFT OUTER JOIN Submissions S on Q.id = S.questionId
    #         WHERE Q.roomId = {roomId} AND Q.isDeleted = FALSE
    #         AND S.isDeleted = FALSE
    #         GROUP BY Q.id
    #     """))

    roomQuestions = db.execute(text(f"""
        SELECT id, title, isVisible
        FROM Questions Q 
        WHERE roomId = {roomId} AND isDeleted = FALSE 
        GROUP BY id
    """))

    questionData = roomQuestions.fetchall()
    questions = []
    for row in questionData:
        print(row)
        questions.append({
            "questionId": row[0],
            "title": row[1],
            "isVisible": row[2],
            "submitted": db.execute(text(f"""
                SELECT COUNT(DISTINCT userId) 
                FROM Submissions 
                WHERE questionId = {row[0]} AND Submissions.isDeleted = FALSE
            """)).fetchone()[0]
        })

    return {"roomInfo": roomInfo, "questions": questions}


def updateRoomById(roomId, roomData, tokenData, db: Session):
    room = db.query(models.Rooms).filter(models.Rooms.id == roomId).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    room.name = roomData.roomName
    room.visibility = roomData.visibility
    room.waitingRoomEnabled = roomData.waitingRoomEnabled

    db.commit()
    db.refresh(room)

    roomInfo = {
        "roomId": room.id,
        "roomName": room.name,
        "visibility": room.visibility,
        "waitingRoomEnabled": room.waitingRoomEnabled,
    }
    myRooms = getMyRooms(tokenData, db)['myRooms']

    return {"roomInfo": roomInfo, "myRooms": myRooms}


