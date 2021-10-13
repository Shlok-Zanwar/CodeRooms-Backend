import json

from fastapi import APIRouter, Depends, Request, HTTPException, status
from Database import database, models
from sqlalchemy.orm import Session
from Functions.Token import getCurrentUser
from pydantic import BaseModel
from typing import Optional, List, Dict
from Functions.QuestionFunctions import createNewQuestion, sendQuestionDetails, saveQuestionTemplate, saveTestCases, \
    saveQuestionSettings, getQuestionForUser, saveCodeForQuestion, getDueQuestions, runCode, submitCodeForQuestion
import time

router = APIRouter(
    tags=['Questions'],
    # prefix="/auth"
)

get_db = database.get_db


class RunCodeSchema(BaseModel):
    code: str
    language: str
    input: str

@router.post('/run_code')
def runGivenCode(
        schema:RunCodeSchema,
        request:Request,
):
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return runCode(schema.language,schema.code, schema.input)


@router.get('/due_questions')
def dueQuestions(
    request: Request,
    db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return getDueQuestions(tokenData, db)


@router.get('/create_question')
def createQuestion(
        roomId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return createNewQuestion(roomId, tokenData, db)


@router.get('/get_question_details')
def getDetails(
        questionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    return sendQuestionDetails(questionId, tokenData, db)


class SaveTemplateSchema(BaseModel):
    questionId: int
    questionTemplate: Dict


@router.post('/save_question_template')
def saveTemplate(
        schema: SaveTemplateSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    # return saveQuestionTemplate(questionId, json.loads(questionTemplate), tokenData, db)
    return saveQuestionTemplate(schema.questionId, schema.questionTemplate, tokenData, db)


class SaveCasesSchema(BaseModel):
    questionId: int
    testCases: List


@router.post('/save_question_tcases')
def saveCases(
        schema: SaveCasesSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    # return saveQuestionTemplate(questionId, json.loads(questionTemplate), tokenData, db)
    return saveTestCases(schema.questionId, schema.testCases, tokenData, db)


class SaveQuestionSettingsSchema(BaseModel):
    questionId: int
    settings: Dict


@router.post('/save_question_settings')
def saveSettings(
        schema: SaveQuestionSettingsSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    # return saveQuestionTemplate(questionId, json.loads(questionTemplate), tokenData, db)
    return saveQuestionSettings(schema.questionId, schema.settings, tokenData, db)


class SaveCodeSchema(BaseModel):
    questionId: int
    code: str
    language: str


@router.post('/save_question_code')
def saveCode(
        schema: SaveCodeSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    # return saveQuestionTemplate(questionId, json.loads(questionTemplate), tokenData, db)
    return saveCodeForQuestion(schema.questionId, schema.code, schema.language, tokenData, db)

@router.post('/submit_question_code')
def saveCode(
        schema: SaveCodeSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    # return saveQuestionTemplate(questionId, json.loads(questionTemplate), tokenData, db)
    return submitCodeForQuestion(schema.questionId, schema.code, schema.language, tokenData, db)


@router.get('/question_user')
def getQuestionUser(
        questionId: int,
        request: Request,
        db: Session = Depends(get_db)
):
    # time.sleep(2)
    try:
        tokenData = getCurrentUser(request.headers['Authorization'])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")

    # return saveQuestionTemplate(questionId, json.loads(questionTemplate), tokenData, db)
    return getQuestionForUser(questionId, tokenData, db)
