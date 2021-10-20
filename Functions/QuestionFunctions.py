import json
import requests
from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from sqlalchemy.sql import text
from datetime import datetime, timedelta
import pytz


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
        print(x.text)
        return x.text


def deleteCurrentQuestion(questionId, tokenData, db):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    if not question.createdBy == tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot delete Question.")

    db.execute(text(f"""
       DELETE  FROM Submissions 
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


def getDueQuestions(tokenData, db: Session):
    allRooms = db.execute(text(f"""
        SELECT roomId FROM RoomMembers WHERE userId = {tokenData['userId']}
    """)).fetchall()

    allQuestions = []
    for room in allRooms:
        q = db.execute(text(f"""
                        SELECT Q.id, Q.roomId, Q.title, Q.endTime, R.name
                        FROM Questions Q 
                        LEFT JOIN Rooms R on R.id = Q.roomId
                        WHERE roomId = {room[0]}
                    """)).fetchall()
        allQuestions.extend(q)

    print(allQuestions)
    dueData = []
    for question in allQuestions:
        print("qid", question[0])
        print(db.execute(text(f"""
                SELECT COUNT(*)
                FROM Submissions S
                WHERE S.userId = {tokenData['userId']} AND S.questionId = {question[0]}
            """)).fetchone()[0])
        if (
                db.execute(text(f"""
                SELECT COUNT(*)
                FROM Submissions S
                WHERE S.userId = {tokenData['userId']} AND S.questionId = {question[0]}
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
        })

    return {"due": questions}


def createNewQuestion(roomId, tokenData, db: Session):
    room = db.query(models.Rooms).filter(models.Rooms.id == roomId).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.isDeleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid room id.")

    if room.ownerId != tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You do not own this room.")

    newQuestion = models.Questions(
        roomId=roomId,
        createdBy=tokenData['userId'],
        title="Title",
        createdAt=datetime.now(pytz.timezone('Asia/Kolkata')),
        template={},
        testCases=[],
        endTime=datetime.now(tz=pytz.timezone('Asia/Kolkata')).replace(hour=23, minute=59, second=59) + timedelta(
            days=7)

    )

    db.add(newQuestion)
    db.commit()
    db.refresh(newQuestion)

    # print(newRoom)
    return {"newQuestionId": newQuestion.id}


def sendQuestionDetails(questionId, tokenData, db: Session):
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

    questionDetails = {
        "id": question.id,
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


def saveQuestionTemplate(questionId, template, tokenData, db: Session):
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

    question.title = template['title']
    question.template = {
        "description": template['description'],
        "sample": template['sample']
    }

    db.commit()
    # db.refresh(question)

    return True


def saveTestCases(questionId, cases, tokenData, db: Session):
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

    question.testCases = cases

    db.commit()

    return True


def saveQuestionSettings(questionId, settings, tokenData, db: Session):
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

    question.endTime = pytz.timezone('Asia/Kolkata').localize(
        datetime.strptime(settings['endTime'], "%Y-%m-%d %H:%M:%S"))
    question.isVisible = settings['isVisible']

    db.commit()

    return True


def submitCodeForQuestion(questionId, code, language, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    casesPassed = 0
    for case in question.testCases:
        if json.loads(runCode(language, code, case['input']))['output'] == case['output']:
            casesPassed += 1

    submittedCode = db.execute(text(f"""
                        SELECT id FROM Submissions 
                        WHERE questionId={questionId} AND userId={tokenData['userId']}
                    """)).fetchone()

    if submittedCode == None:
        newEntry = models.Submissions(
            userId=tokenData['userId'],
            questionId=questionId,
            code=code,
            submittedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
            language=language,
            testCasesPassed=casesPassed,
        )
        db.add(newEntry)
        db.commit()
        # db.refresh(newEntry)
    else:
        db.execute(text(f"""
                                DELETE FROM Submissions WHERE id = {submittedCode[0]}
                            """))

        newEntry = models.Submissions(
            userId=tokenData['userId'],
            questionId=questionId,
            code=code,
            submittedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
            language=language,
            testCasesPassed=casesPassed,
        )
        db.add(newEntry)
        db.commit()

    saveCodeForQuestion(questionId, code, language, tokenData, db)

    return f"{casesPassed} out of {len(question.testCases)} cases passed."


def saveCodeForQuestion(questionId, code, language, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

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
        # db.refresh(newEntry)
    else:
        db.execute(text(f"""
                            DELETE FROM SavedCodes WHERE id = {savedCode[0]}
                        """))

        newEntry = models.SavedCodes(
            userId=tokenData['userId'],
            questionId=questionId,
            code=code,
            savedAt=datetime.now(pytz.timezone('Asia/Kolkata')),
            language=language
        )
        db.add(newEntry)
        db.commit()

        # db.execute(text(f"""
        #                     UPDATE SavedCodes
        #                     SET code = {code},
        #                     savedAt = {datetime.now(pytz.timezone('Asia/Kolkata'))},
        #                     language = {language}
        #                     WHERE id={savedCode[0]}
        #                 """))
        # db.commit()

    return True


def getQuestionForUser(questionId, tokenData, db: Session):
    question = db.query(models.Questions).filter(models.Questions.id == questionId).first()

    if not question or not question.isVisible:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    room = db.query(models.Rooms).filter(models.Rooms.id == question.roomId).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room does not exist.")

    if room.isDeleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid room id.")

    if room.ownerId == tokenData['userId']:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"You cannot answer your question.")

    isAllowed = db.execute(text(f"""
                SELECT * FROM RoomMembers 
                WHERE roomId={question.roomId} AND userId={tokenData['userId']} AND isRejected=FALSE AND inWaitingRoom=FALSE
            """)).fetchone()

    if not isAllowed:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid question Id.")

    savedCode = db.execute(text(f"""
                SELECT code, language FROM SavedCodes 
                WHERE questionId={questionId} AND userId={tokenData['userId']}
            """)).fetchone()

    if not savedCode:
        code = ""
        language = "cpp"
    else:
        code = savedCode[0]
        language = savedCode[1]

    questionDetails = {
        "id": question.id,
        "roomId": question.roomId,
        "roomName": room.name,
        "endTime": question.endTime,
        "title": question.title,
        "template": question.template,
        "savedCode": code,
        "language": language
    }

    return {"details": questionDetails}


# C++	cpp
# C	    c
# C#	cs
# Java	java
# Python	py
# Ruby	rb
# Kotlin	kt
# Swift	swift


a = a = {
    "description": {
        "blocks": [
            {
                 "key": "aliq6",
                 "text": "Add 2 to input",
                 "type": "unstyled",
                 "depth": 0,
                 "inlineStyleRanges": [
                      {
                         "offset": 4,
                         "length": 1,
                         "style": "BOLD"
                      },
                      {
                          "offset": 4,
                          "length": 1,
                          "style": "ITALIC"
                      },
                      {
                          "offset": 4,
                          "length": 1,
                          "style": "UNDERLINE"
                      },
                      {
                          "offset": 4,
                          "length": 1,
                          "style": "CODE"
                      }
                 ],
                 "entityRanges": [],
                 "data": {}
            },
            {
                "key": "f0qgo",
                "text": "",
                "type": "unstyled",
                "depth": 0,
                "inlineStyleRanges": [],
                "entityRanges": [],
                "data": {}
            }
        ],
        "entityMap": {}
    },
}
