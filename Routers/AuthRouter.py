from fastapi import APIRouter, Depends, Request
from Database import database
from sqlalchemy.orm import Session
from pydantic import BaseModel
from Functions.AuthFunctions import handleLogin, createSignUp, verifyEmail, reqChangePassword, changePassword, \
    changeUsername, resendVerifyEmail, changeAccountType
from Functions.MiscFunctions import verifyJWTToken

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


@router.get('/request_change_password')
def postReqChangePassword(email: str, db: Session = Depends(get_db)):
    return reqChangePassword(email, db)


class ChangePasswordSchema (BaseModel):
    email: str
    password: str
    otp: str

@router.post('/change_password')
def postChangePassword(request: ChangePasswordSchema, db: Session = Depends(get_db)):
    return changePassword(request, db)


class ChangeUsernameSchema (BaseModel):
    userName: str

@router.post('/change_username')
def postChangeUsername(
        schema: ChangeUsernameSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return changeUsername(schema.userName, tokenData, db)

@router.get('/resend_verification_link')
def getResendVerifyEmail(
        username: str,
        db: Session = Depends(get_db)
):
    return resendVerifyEmail(username, db)


class ChangeAccountTypeSchema (BaseModel):
    userId: int
    accountType: int

@router.post('/change_account_type')
def postChangeAccountType(
        schema: ChangeAccountTypeSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    tokenData = verifyJWTToken(request)
    return changeAccountType(schema.userId, schema.accountType, tokenData, db)
