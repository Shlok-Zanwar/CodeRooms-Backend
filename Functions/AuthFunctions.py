from sqlalchemy.orm import Session
from Database import models
from fastapi import HTTPException, status
from Functions.HashPassword import bcryptPassword, verifyPassword
from Functions.Token import createAccessToken
from email.message import EmailMessage
import smtplib, ssl
import random
from sqlalchemy.sql import text


def sendOtp(email):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "projectforms1@gmail.com"
    password = "Pforms@123"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)

        otp = random.randint(100000, 999999)
        message = f"Verify your account for CodeRooms.\nClick :- http://localhost:3000/verify_email?email={email}&otp={str(otp)}"
        # print(otp)

        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = 'Verify Account.'
        msg['From'] = sender_email
        msg['To'] = email
        server.send_message(msg)
        # server.sendmail(sender_email, receiver_email, message)
        server.quit()
        return otp

    except Exception as e:
        # Print any error messages to stdout
        print(e)

def createSignUp(request, db: Session):
    newUser = models.User(
            name = request.name,
            email = request.email,
            password = bcryptPassword(request.password),
            username = request.username,
            otp = sendOtp(request.email),
            isVerified = False
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
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email does not exist.")

    if user.isVerified:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Email already verified.")

    if request.otp == user.otp:
        user.isVerified = True
        user.otp = None
        user._try = 0
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"detail": "Verified account."}


    elif user._try == 2:
        user.otp = sendOtp(request.email)
        user._try = 0
        db.add(user)
        db.commit()
        db.refresh(user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid OTP 0 tries left. Sending new OTP to {user.email}")

    else:
        user._try = user._try + 1
        db.add(user)
        db.commit()
        db.refresh(user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid OTP {3-user._try} tries left.")

def handleLogin(request, db: Session):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Username does not exist.")

    if not user.isVerified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Please verify your account.")

    if not verifyPassword(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Incorrect password.")

    # a = db.execute(text("SELECT * FROM Users"))
    # print(a.fetchone()[1])

    access_token = createAccessToken( data={"userName": user.username, "userId": user.id} )
    return {"access_token": access_token, "token_type": "bearer" }
