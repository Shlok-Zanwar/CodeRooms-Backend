from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from sqlalchemy.sql import text
from datetime import datetime, timedelta
import pytz
from Functions.MyRoomsFunctions import verifyRoomOwner
import json
import os
import glob

emptyDescription = {
    "blocks": [
        {   "key": "7ioug",
            "text": "",
            "type": "unstyled",
            "depth": 0,
            "inlineStyleRanges": [],
            "entityRanges": [],
            "data": {}
        }
    ],
    "entityMap": {}
}


def createNewQuestion(roomId, type, tokenData, db: Session):

    newQuestion = models.Questions(
        roomId = roomId,
        createdBy = tokenData['userId'],
        title = "Title",
        createdAt = datetime.now(pytz.timezone('Asia/Kolkata')),
        template = {
            "description": emptyDescription,
            "sample": {
                "input": "",
                "output": "",
                "explanation": "",
            },
        },
        testCases = [],
        _type = type,
        endTime = datetime.now(tz=pytz.timezone('Asia/Kolkata')).replace(hour=23, minute=59, second=59) + timedelta(days=7)
    )

    db.add(newQuestion)
    db.commit()
    db.refresh(newQuestion)

    if type == "file":
        os.mkdir("SavedFiles/Q_" + str(newQuestion.id))

    return {"newQuestionId": newQuestion.id}


def getQuestionDetails(questionId, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()
    if not question or question.createdBy != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = verifyRoomOwner(question.roomId, tokenData, db)

    questionDetails = {
        "id": question.id,
        "_type": question._type,
        "roomId": question.roomId,
        "roomName": room.name,
        "endTime": question.endTime,
        "isVisible": question.isVisible,
        "title": question.title,
        "template": question.template,
        "testCases": question.testCases,
        "submissionCountAllowed": question.submissionCountAllowed,
    }

    return {"questionDetails": questionDetails}


def saveQuestionTemplate(questionId, title, template, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or question.createdBy != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    question.title = title
    question.template = template

    db.commit()
    return True


def saveTestCases(questionId, cases, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or question.createdBy != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot delete Question.")

    question.testCases = cases

    db.commit()
    return True


def saveQuestionSettings(questionId, endTime, isVisible, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or question.createdBy != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot delete Question.")

    a = pytz.timezone('Asia/Kolkata').localize(datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S"))
    print(a)
    question.endTime = a
    question.isVisible = isVisible

    db.commit()

    return True


def deleteQuestion(questionId, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or question.createdBy != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid Question Id.")

    if question._type == "file":

        dir = os.getcwd() + f"/SavedFiles/Q_{questionId}"
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        os.removedirs(dir)

        db.execute(text(f"""
            DELETE FROM FileSubmissions 
            WHERE questionId={questionId}
        """))

    else:
        db.execute(text(f"""
           DELETE  FROM CodeSubmissions
           WHERE questionId={questionId}
       """))
        db.execute(text(f"""
           DELETE  FROM SavedCodes
           WHERE questionId={questionId}
       """))

    db.execute(text(f"""
        DELETE FROM Questions
        WHERE id={questionId}
    """))
    db.commit()
    return True


def getQuestionSubmission(questionId, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = verifyRoomOwner(question.roomId, tokenData, db)

    roomDetails = {
        "roomName": room.name,
        "roomId": room.id,
        "specialFields": room.specialFields
    }

    questionDetails = {
        "title": question.title,
        "template": question.template,
        "endTime": question.endTime,
        "testCases": len(question.testCases),
        "_type": question._type,
    }

    roomMembers = db.execute(text(f"""
                        SELECT U.id, U.username, U.email, U.fname, U.lname, Rm.specialFields
                        FROM RoomMembers RM
                        LEFT JOIN Users U on U.id = RM.userId
                        WHERE RM.roomId = {room.id} AND RM.isRejected = FALSE AND RM.inWaitingRoom = FALSE
                        GROUP BY U.id
                    """)).fetchall()
    # print(roomMembers)

    members = []
    if question._type == "code":
        for member in roomMembers:
            subData = db.execute(text(f"""
                            SELECT id, testCasesPassed, submittedAt 
                            FROM CodeSubmissions 
                            WHERE userId={member[0]} AND questionId = {questionId}
                        """)).fetchone()

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

    elif question._type == "file":
        for member in roomMembers:
            subData = db.execute(text(f"""
                            SELECT id, submittedAt 
                            FROM FileSubmissions 
                            WHERE userId={member[0]} AND questionId = {questionId}
                        """)).fetchone()

            if not subData:
                subId = 0
                stime = 0
            else:
                subId = subData[0]
                stime = subData[1]

            members.append({
                "userId": member[0],
                "userName": member[1],
                "email": member[2],
                "name": member[3] + " " + member[4],
                "specialFields": json.loads(member[5]),
                "submissionId": subId,
                "submittedAt": stime
            })

    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Some error occured.")


    return {"roomDetails": roomDetails, "questionDetails": questionDetails, "enrolled": members}


def getSubmittedCode(subId, db: Session):
    # submission = db.query(models.Submissions).filter(models.Submissions.id == subId).first()
    subData = db.execute(text(f"""
                            SELECT code, language FROM CodeSubmissions WHERE id={subId}
                        """)).fetchone()

    if not subData:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid submission Id.")

    data = {
        "code": subData.code,
        "language": subData.language,
    }

    return {"data": data}


