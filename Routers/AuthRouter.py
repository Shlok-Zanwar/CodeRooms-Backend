from fastapi import APIRouter, Depends
from Database import database
from sqlalchemy.orm import Session
from pydantic import BaseModel
from Functions.AuthFunctions import handleLogin, createSignUp, verifyEmail

router = APIRouter(
    tags=['Auths'],
    prefix="/auth"
)
get_db = database.get_db


class UserSignupSchema (BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str
    username: str

@router.post('/signup')
def postSignup(request: UserSignupSchema, db: Session = Depends(get_db)):
    return createSignUp(request, db)



class VerifyEmailSchema (BaseModel):
    email: str
    otp: str

@router.post('/verify_email')
def postVerifyEmail(request: VerifyEmailSchema, db: Session = Depends(get_db)):
    return verifyEmail(request, db)



class UserLoginSchema (BaseModel):
    username: str
    password: str

@router.post('/login')
def postLogin(request: UserLoginSchema, db: Session = Depends(get_db)):
    return handleLogin(request, db)
