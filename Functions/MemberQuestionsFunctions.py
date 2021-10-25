import json
import os
from os import getenv
import requests
from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from sqlalchemy.sql import text
from datetime import datetime
import pytz

def questionForMember(questionId, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = db.query(models.Rooms).filter(models.Rooms.id == question.roomId).first()
    if not room or room.visibility == "hidden":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid question Id.")

    isAllowed = db.execute(text(f"""
                SELECT id FROM RoomMembers 
                WHERE roomId={question.roomId} AND userId={tokenData['userId']} 
                AND isRejected = FALSE AND inWaitingRoom = FALSE
            """)).fetchone()
    if not isAllowed:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    if question._type == "code":
        savedCode = db.execute(text(f"""
                    SELECT code, language FROM SavedCodes 
                    WHERE questionId={questionId} AND userId={tokenData['userId']}
                """)).fetchone()

        submittedCode = db.execute(text(f"""
                    SELECT submittedAt FROM CodeSubmissions 
                    WHERE questionId={questionId} AND userId={tokenData['userId']}
                """)).fetchone()

        questionDetails = {
            "id": question.id,
            "roomId": question.roomId,
            "roomName": room.name,
            "endTime": question.endTime,
            "title": question.title,
            "template": json.loads(question.template),
            "_type": question._type,
            "submitted": False
        }

        if not savedCode:
            questionDetails['savedCode'] = ""
            questionDetails['language'] = "cpp"

        else:
            questionDetails['savedCode'] = savedCode[0]
            questionDetails['language'] = savedCode[1]

            if submittedCode:
                questionDetails['submitted'] = True
                questionDetails['submittedAt'] = submittedCode[0]


        return {"details": questionDetails}

    elif question._type == "file":
        questionDetails = {
            "id": question.id,
            "roomId": question.roomId,
            "roomName": room.name,
            "endTime": question.endTime,
            "title": question.title,
            "template": json.loads(question.template),
            "_type": question._type,
            "submitted": False
        }

        submittedFile = db.execute(text(f"""
                            SELECT submittedAt, id FROM FileSubmissions 
                            WHERE questionId={questionId} AND userId={tokenData['userId']}
                        """)).fetchone()

        if submittedFile:
            questionDetails['submitted'] = True
            questionDetails['submittedAt'] = submittedFile[0]
            questionDetails['submissionId'] = submittedFile[1]



        return {"details": questionDetails}

    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Some error occured.")


def getDueQuestions(tokenData, db: Session):
    allRooms = db.execute(text(f"""
        SELECT roomId FROM RoomMembers WHERE userId = {tokenData['userId']}
    """)).fetchall()

    allQuestions = []
    for room in allRooms:

        q = db.execute(text(f"""
                        SELECT Q.id, Q.roomId, Q.title, Q.endTime, R.name, Q._type
                        FROM Questions Q 
                        LEFT JOIN Rooms R on R.id = Q.roomId
                        WHERE roomId = {room[0]} AND Q.isVisible = TRUE
                    """)).fetchall()
        allQuestions.extend(q)

    dueData = []
    for question in allQuestions:
        if datetime.now(pytz.timezone('Asia/Kolkata')) > pytz.timezone('Asia/Kolkata').localize(datetime.strptime(question[3], "%Y-%m-%d %H:%M:%S.%f")):
            continue

        if question[5] == "code":
            if (
                db.execute(text(f"""
                    SELECT COUNT(*)
                    FROM CodeSubmissions
                    WHERE userId = {tokenData['userId']} AND questionId = {question[0]}
                """)).fetchone()[0] == 0
            ):
                dueData.append(question)
        else:
            if (
                db.execute(text(f"""
                    SELECT COUNT(*)
                    FROM FileSubmissions
                    WHERE userId = {tokenData['userId']} AND questionId = {question[0]}
                """)).fetchone()[0] == 0
            ):
                dueData.append(question)

    questions = []
    for question in dueData:
        questions.append({
            "questionId": question[0],
            "roomId": question[1],
            "title": question[2],
            "endTime": question[3],
            "roomName": question[4],
            "_type": question[5]
        })

    return {"due": questions}


def runCode(language, code, input):
    if language == "python":
        language = "py"

    url = 'https://codexweb.netlify.app/.netlify/functions/enforceCode'
    myobj = {
        "code": code,
        "language": language,
        "input": input
    }

    x = requests.post(
        url,
        data=json.dumps(myobj),
        headers={
            'Content-Type': 'application/json'
        }
    )

    if x.status_code == 200:
        return x.text


def saveCodeForQuestion(questionId, code, language, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = db.query(models.Rooms).filter(models.Rooms.id == question.roomId).first()
    if not room or room.visibility == "hidden":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid question Id.")

    isAllowed = db.execute(text(f"""
                    SELECT id FROM RoomMembers 
                    WHERE roomId={question.roomId} AND userId={tokenData['userId']} 
                    AND isRejected = FALSE AND inWaitingRoom = FALSE
                """)).fetchone()
    if not isAllowed:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    # db.query(models.SavedCodes).filter((models.SavedCodes.questionId == questionId) & (models.SavedCodes.userId == tokenData['userId']) ).update(
    #     {
    #         "code": code,
    #         "language": language
    #     }
    # )
    # db.commit()

    savedCode = db.execute(text(f"""
                    SELECT id FROM SavedCodes
                    WHERE questionId={questionId} AND userId={tokenData['userId']}
                """)).fetchone()


    if savedCode == None:
        newEntry = models.SavedCodes(
            userId=tokenData['userId'],
            questionId=questionId,
            code=code,
            savedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
            language=language
        )
        db.add(newEntry)
        db.commit()
    else:
        db.query(models.SavedCodes).filter_by(questionId = questionId, userId = tokenData['userId'] ).update(
            {
                "code": code,
                "language": language
            }
        )
        db.commit()


    return True


def submitCodeForQuestion(questionId, code, language, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = db.query(models.Rooms).filter(models.Rooms.id == question.roomId).first()
    if not room or room.visibility == "hidden":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid question Id.")

    isAllowed = db.execute(text(f"""
                        SELECT id FROM RoomMembers 
                        WHERE roomId={question.roomId} AND userId={tokenData['userId']} 
                        AND isRejected = FALSE AND inWaitingRoom = FALSE
                    """)).fetchone()
    if not isAllowed:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    # print(question.endTime)
    if datetime.now(pytz.timezone('Asia/Kolkata')) > pytz.timezone('Asia/Kolkata').localize(question.endTime):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Due date over")


    casesPassed = 0
    for case in json.loads(question.testCases):
        if json.loads(runCode(language, code, case['input']))['output'] == case['output']:
            casesPassed += 1

    submittedCode = db.execute(text(f"""
                        SELECT id FROM CodeSubmissions 
                        WHERE questionId={questionId} AND userId={tokenData['userId']}
                    """)).fetchone()

    if submittedCode == None:
        newEntry = models.CodeSubmissions(
            userId=tokenData['userId'],
            questionId=questionId,
            code=code,
            submittedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
            language=language,
            testCasesPassed=casesPassed,
        )
        db.add(newEntry)
        db.commit()
    else:
        db.query(models.CodeSubmissions).filter_by(questionId=questionId, userId=tokenData['userId']).update(
            {
                "code": code,
                "language": language
            }
        )
        db.commit()

    saveCodeForQuestion(questionId, code, language, tokenData, db)

    return {"casesPassed": casesPassed, "noOfCases": len(json.loads(question.testCases))}
    # return f"{casesPassed} out of {len(question.testCases)} cases passed."


def deleteSubmittedFile(questionId, submissionId, tokenData, db: Session):
    userData = db.execute(text(f"""
        SELECT userId from FileSubmissions
        WHERE id={submissionId}
    """)).fetchone()
    if not userData:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid submission Id.")
    elif userData[0] != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You donot have acceess.")


    if os.path.exists(getenv("BASE_PATH") + f"/SavedFiles/Q_{questionId}/SID_{submissionId}.pdf"):
        os.remove(getenv("BASE_PATH") + f"/SavedFiles/Q_{questionId}/SID_{submissionId}.pdf")
        db.execute(text(f"""
                        DELETE FROM FileSubmissions 
                        WHERE id={submissionId}
                    """))
        db.commit()
        return True
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"File does not exist.")



def submitFileForQuestion(questionId, file, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = db.query(models.Rooms).filter(models.Rooms.id == question.roomId).first()
    if not room or room.visibility == "hidden":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid question Id.")

    isAllowed = db.execute(text(f"""
                        SELECT id FROM RoomMembers
                        WHERE roomId={question.roomId} AND userId={tokenData['userId']}
                        AND isRejected = FALSE AND inWaitingRoom = FALSE
                    """)).fetchone()
    if not isAllowed:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    # print(question.endTime)
    if datetime.now(pytz.timezone('Asia/Kolkata')) > pytz.timezone('Asia/Kolkata').localize(question.endTime):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Due date over")


    newEntry = models.FileSubmissions(
        userId=tokenData['userId'],
        questionId=questionId,
        submittedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
        fileName = file.filename
    )
    db.add(newEntry)
    db.commit()
    db.refresh(newEntry)

    file_name = getenv("BASE_PATH") + f"/SavedFiles/Q_{questionId}/SID_{newEntry.id}.pdf"
    with open(file_name, 'wb+') as f:
        f.write(file.file.read())
        f.close()


    return {"submissionId": newEntry.id}
