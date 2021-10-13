import json

from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from Functions.Token import getCurrentUser
from sqlalchemy.sql import text
from datetime import datetime
import random
import pytz


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


def createNewRoom(tokenData, db: Session):
    newRoom = models.Rooms(
        ownerId = tokenData['userId'],
        name = "New Room" + str(random.randint(1, 100)),
        createdAt = datetime.now(pytz.timezone('Asia/Kolkata')),
        specialFields = []
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
        SELECT id, ownerId, name, visibility, waitingRoomEnabled, specialFields
        FROM Rooms
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
        "waitingRoomCount": getWaitingRoomCount(roomId, db),
        "specialFields": json.loads(sqlData[5])
    }

    roomQuestions = db.execute(text(f"""
        SELECT id, title, isVisible, endTime
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
            "endTime": row[3],
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

    if room.isDeleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid room id.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    # print(roomData)
    room.name = roomData.roomName
    room.visibility = roomData.visibility
    room.waitingRoomEnabled = roomData.waitingRoomEnabled
    room.specialFields = roomData.specialFields

    db.commit()
    db.refresh(room)

    if not roomData.waitingRoomEnabled:
        members = db.execute(text(f"""
                    SELECT id FROM RoomMembers 
                    WHERE roomId = {roomId} AND inWaitingRoom = TRUE AND isRejected = FALSE 
                """)).fetchall()


        for member in members:
            print(member)
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
        "enrolled": getEnrolledCount(roomId, db),
        "waitingRoomCount": getWaitingRoomCount(roomId, db)
    }
    myRooms = getMyRooms(tokenData, db)['myRooms']

    return {"roomInfo": roomInfo, "myRooms": myRooms}


def getRoomMembers(roomId, tokenData, waiting, db: Session, ):
    room = db.query(models.Rooms).filter(models.Rooms.id == roomId).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.isDeleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid room id.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    roomMembers = db.execute(text(f"""
                    SELECT U.id, U.username, U.email, U.fname, U.lname, Rm.id, Rm.specialFields
                    FROM RoomMembers RM
                    LEFT JOIN Users U on U.id = RM.userId
                    WHERE RM.roomId = {roomId} AND RM.isRejected = FALSE AND RM.inWaitingRoom = {waiting}
                    GROUP BY U.id
                """)).fetchall()

    members = []
    for member in roomMembers:
        members.append({
            "userId": member[0],
            "userName": member[1],
            "email": member[2],
            "name": member[3] + " " + member[4],
            "tableId": member[5],
            "specialFields": json.loads(member[6])
        })

    return members


def getSubmittedCode(subId, db: Session):
    # submission = db.query(models.Submissions).filter(models.Submissions.id == subId).first()
    subData = db.execute(text(f"""
                            SELECT code, language FROM Submissions WHERE id={subId}
                        """)).fetchone()

    if not subData:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid submission Id.")

    data = {
        "code": subData.code,
        "language": subData.language,
    }

    return {"data": data}


def getQuestionSubmission(questionId, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = db.query(models.Rooms).filter(models.Rooms.id == question.roomId).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.isDeleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid room id.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this question.")


    roomDetails = {
        "roomName": room.name,
        "roomId": room.id,
        "specialFields": room.specialFields
    }
    questionDetails = {
        "title": question.title,
        "template": question.template,
        "endTime": question.endTime,
        "testCases": len(question.testCases)
    }

    roomMembers = db.execute(text(f"""
                        SELECT U.id, U.username, U.email, U.fname, U.lname, Rm.specialFields
                        FROM RoomMembers RM
                        LEFT JOIN Users U on U.id = RM.userId
                        WHERE RM.roomId = {room.id} AND RM.isRejected = FALSE AND RM.inWaitingRoom = FALSE
                        GROUP BY U.id
                    """)).fetchall()
    print(roomMembers)

    members = []
    for member in roomMembers:
        subData = db.execute(text(f"""
                        SELECT id, testCasesPassed, submittedAt FROM Submissions WHERE userId={member[0]} AND questionId = {questionId}
                    """)).fetchone()

        print(subData)

        if not subData:
            subId = 0
            tCasesPassed = 0
            stime = 0
        else:
            subId = subData[0]
            tCasesPassed = subData[1]
            stime = subData[2]

        members.append({
            "userId": member[0],
            "userName": member[1],
            "email": member[2],
            "name": member[3] + " " + member[4],
            "specialFields": json.loads(member[5]),
            "submissionId": subId,
            "tCasesPassed": tCasesPassed,
            "submittedAt": stime
        })

    return {"roomDetails": roomDetails, "questionDetails": questionDetails, "enrolled": members}


def modifyRoomMember(roomId, userId, tokenData, reject, db: Session):
    room = db.query(models.Rooms).filter(models.Rooms.id == roomId).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.isDeleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid room id.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    db.execute(text(f"""
                        UPDATE RoomMembers
                        SET isRejected = {reject}, inWaitingRoom = FALSE
                        WHERE userId = {userId} AND roomId = {roomId}
                    """))
    db.commit()

    return True

