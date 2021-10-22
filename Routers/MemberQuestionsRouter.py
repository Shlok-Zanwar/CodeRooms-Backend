from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy import text
from Database import database
from sqlalchemy.orm import Session
from Functions.MiscFunctions import verifyJWTToken, decodeJWTToken, credentialsException
from pydantic import BaseModel
from Functions.MemberQuestionsFunctions import questionForMember, getDueQuestions, runCode,\
    saveCodeForQuestion, submitCodeForQuestion, submitFileForQuestion, deleteSubmittedFile
import os
from fastapi.responses import FileResponse

router = APIRouter(
    tags=['Member Questions'],
)

get_db = database.get_db


@router.get('/question_for_member')
def questionForMemberRoute(
        questionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return questionForMember(questionId, tokenData, db)


@router.get('/due_questions')
def dueQuestionsRoute(
    request: Request,
    db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getDueQuestions(tokenData, db)



class RunCodeSchema(BaseModel):
    code: str
    language: str
    input: str

@router.post('/run_code')
def runCodeRoute(
        schema: RunCodeSchema,
        request:Request,
):
    tokenData = verifyJWTToken(request)
    return runCode(schema.language, schema.code, schema.input)



class SaveCodeSchema(BaseModel):
    questionId: int
    code: str
    language: str


@router.post('/save_question_code')
def saveCodeRoute(
        schema: SaveCodeSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return saveCodeForQuestion(schema.questionId, schema.code, schema.language, tokenData, db)

@router.post('/submit_question_code')
def submitCodeRoute(
        schema: SaveCodeSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return submitCodeForQuestion(schema.questionId, schema.code, schema.language, tokenData, db)



@router.post('/submit_question_file/{questionId}')
def uploadFileRoute(
    questionId,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print(file)
    print(questionId)

    tokenData = verifyJWTToken(request)
    return submitFileForQuestion(questionId, file, tokenData, db)



class DeleteFileSchema(BaseModel):
    questionId: int
    submissionId: int

@router.post('/delete_submitted_file')
def uploadFileRoute(
    schema: DeleteFileSchema,
    request: Request,
    db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return deleteSubmittedFile(schema.questionId, schema.submissionId, tokenData, db)


@router.get('/get_submitted_file')
def uploadFileRoute(
    questionId: int,
    submissionId: int,
    token: str,
    db: Session = Depends(get_db)
):
    tokenData = decodeJWTToken(token)
    sqlData = db.execute(text(f"""
                SELECT userId, questionId FROM FileSubmissions 
                WHERE id={submissionId} 
            """)).fetchone()
    if not sqlData:
        raise credentialsException
    else:
        if sqlData[0] == tokenData['userId']:
            return FileResponse(os.getcwd() + f"/SavedFiles/Q_{questionId}/SID_{submissionId}.pdf")
        else:
            data2 = db.execute(text(f"""
                        SELECT createdBy FROM Questions 
                        WHERE id={sqlData[1]}
                    """)).fetchone()
            if not data2:
                raise credentialsException
            else:
                if data2[0] == tokenData['userId']:
                    return FileResponse(os.getcwd() + f"/SavedFiles/Q_{questionId}/SID_{submissionId}.pdf")
                else:
                    raise credentialsException

