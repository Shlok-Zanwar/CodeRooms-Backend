import pytz
from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from Functions.HashPassword import bcryptPassword, verifyPassword
from Functions.Token import createAccessToken
from email.message import EmailMessage
import smtplib, ssl
import random
from datetime import datetime


def sendMail(message):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    message['From'] = "projectforms1@gmail.com"
    password = "Pforms@123"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(message['From'], password)

        server.send_message(message)
        # server.sendmail(sender_email, receiver_email, message)
        server.quit()

    except Exception as e:
        # Print any error messages to stdout
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to send OTP.")


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
        # db.add(user)
        db.commit()
        db.refresh(user)
        return {"detail": "Verified account."}


    elif user._try == 2:
        user.otp = sendOtp(request.email)
        user._try = 0
        # db.add(user)
        db.commit()
        db.refresh(user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid OTP. Sending new OTP to {user.email}")

    else:
        user._try = user._try + 1
        # db.add(user)
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

    # a = db.execute(text("SELECT * FROM Users"))
    # print(a.fetchone()[1])

    access_token = createAccessToken( data={"userName": user.username, "userId": user.id, "firstName": user.fname, "lastName": user.lname} )
    return {"access_token": access_token, "token_type": "bearer" }
