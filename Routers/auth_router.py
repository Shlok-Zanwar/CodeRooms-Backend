from fastapi import APIRouter, Depends, Request
from Database import database, models
from sqlalchemy.orm import Session
from Functions import AuthFunctions
from pydantic import BaseModel
from typing import  Optional, List

router = APIRouter(
    tags=['Auth'],
    prefix="/auth"
)

get_db = database.get_db


class UserSignupSchema (BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str
    username: str

class UserLoginSchema (BaseModel):
    username: str
    password: str

class VerifyEmailSchema (BaseModel):
    email: str
    otp: str


@router.post('/login')
def handleLogin(
        # request: Request
        request: UserLoginSchema,
        db: Session = Depends(get_db)
):
    return AuthFunctions.handleLogin(request, db)


@router.post('/signup')
def handleSignUp(
    # request: Request,
    request: UserSignupSchema,
    db: Session = Depends(get_db)
):
    return AuthFunctions.createSignUp(request, db)

import time
@router.post('/verify_email')
def verifyEmail(
    # request: Request,
    request: VerifyEmailSchema,
    db: Session = Depends(get_db)
):
    time.sleep(2)
    return AuthFunctions.verifyEmail(request, db)


