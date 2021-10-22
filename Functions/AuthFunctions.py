import pytz
from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from Functions.MiscFunctions import sendMail, bcryptPassword, verifyPassword, createAccessToken
from email.message import EmailMessage
import random
from datetime import datetime


def sendOtp(email):
    otp = random.randint(100000, 999999)
    message = f"Verify your account for CodeRooms.\nClick :- http://localhost:3000/verify_email?email={email}&otp={str(otp)}"
    # print(otp)

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'Verify Account.'
    msg['To'] = email

    sendMail(msg)
    return otp


def createSignUp(request, db: Session):
    newUser = models.Users(
            fname = request.firstName,
            lname = request.lastName,
            email = request.email,
            password = bcryptPassword(request.password),
            username = request.username,
            otp = sendOtp(request.email),
            isVerified = False,
            createdAt = datetime.now(pytz.timezone('Asia/Kolkata'))
        )

    try:
        db.add(newUser)
        db.commit()
        db.refresh(newUser)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Username or email already exists.")

    return newUser


def verifyEmail(request, db: Session):
    user = db.query(models.Users).filter(models.Users.email == request.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email does not exist.")

    if user.isVerified:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Email already verified.")

    if request.otp == user.otp:
        user.isVerified = True
        user.otp = None
        user._try = 0
        user.verifiedAt = datetime.now(pytz.timezone('Asia/Kolkata'))

        db.commit()
        db.refresh(user)
        return {"detail": "Verified account."}


    elif user._try == 2:
        user.otp = sendOtp(request.email)
        user._try = 0

        db.commit()
        db.refresh(user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid OTP. Sending new OTP to {user.email}")

    else:
        user._try = user._try + 1

        db.commit()
        db.refresh(user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid OTP {3-user._try} tries left.")


def handleLogin(request, db: Session):
    user = db.query(models.Users).filter(models.Users.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Username does not exist.")

    if not user.isVerified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Please verify your account.")

    if not verifyPassword(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Incorrect password.")

    access_token = createAccessToken(
        data={
            "userName": user.username,
            "userId": user.id,
            "firstName": user.fname,
            "lastName": user.lname
        }
    )
    return {"access_token": access_token, "token_type": "bearer" }

