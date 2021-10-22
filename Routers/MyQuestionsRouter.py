from fastapi import APIRouter, Depends, Request
from Database import database
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict
from Functions.MyQuestionsFunctions import createNewQuestion, getQuestionDetails, saveQuestionTemplate, \
    saveTestCases, saveQuestionSettings, deleteQuestion, getSubmittedCode, getQuestionSubmission
from Functions.MiscFunctions import verifyJWTToken
from Functions.MyRoomsFunctions import verifyRoomOwner

router = APIRouter(
    tags=['Questions'],
)

get_db = database.get_db


class createQuestionSchema(BaseModel):
    roomId: int
    type: str
    #- type: Literal["code", "file"]

@router.post('/create_question')
def CreateNewQuestionRoute(
        questionInfo: createQuestionSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    verifyRoomOwner(questionInfo.roomId, tokenData, db)
    return createNewQuestion(questionInfo.roomId, questionInfo.type, tokenData, db)


@router.get('/get_question_details')
def getQuestionDetailsRoute(
        questionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    # verifyRoomOwner(questionId, tokenData, db)                            # Verified inside
    return getQuestionDetails(questionId, tokenData, db)



class SaveTemplateSchema(BaseModel):
    questionId: int
    title: str
    template: Dict

@router.post('/save_question_template')
def saveTemplateRoute(
        schema: SaveTemplateSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return saveQuestionTemplate(schema.questionId, schema.title, schema.template, tokenData, db)



class SaveCasesSchema(BaseModel):
    questionId: int
    testCases: List

@router.post('/save_question_tcases')
def saveTestCasesRoute(
        schema: SaveCasesSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return saveTestCases(schema.questionId, schema.testCases, tokenData, db)



class SaveQuestionSettingsSchema(BaseModel):
    questionId: int
    endTime: str
    isVisible: bool

@router.post('/save_question_settings')
def saveQuestionSettingsRoute(
        schema: SaveQuestionSettingsSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return saveQuestionSettings(schema.questionId, schema.endTime, schema.isVisible, tokenData, db)



class DeleteQuestionSchema(BaseModel):
    questionId: int

@router.post('/delete_question')
def deleteQuestionRoute(
        schema: DeleteQuestionSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return deleteQuestion(schema.questionId, tokenData, db)


@router.get("/question_submissions")
def questionSubmissions(
        questionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getQuestionSubmission(questionId, tokenData, db)

@router.get("/get_submitted_code")
def submittedCodeGet(
        submissionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return getSubmittedCode(submissionId, db)