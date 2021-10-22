from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
import smtplib, ssl

# Inportant Constants
SECRET_KEY = "ApnaSecretBhidu"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5000
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
credentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

myEmailId = "projectforms1@gmail.com"
myEmailPassword = "Pforms@123"


# Token Functions
def createAccessToken(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decodeJWTToken(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentialsException


def verifyJWTToken(request):
    try:
        tokenData = decodeJWTToken(request.headers['Authorization'])
    except:
        raise credentialsException

    return tokenData


# Hash Password functions
def bcryptPassword(password: str):
    return pwd_cxt.hash(password)


def verifyPassword(hashed_password, plain_password):
    return pwd_cxt.verify(plain_password, hashed_password)


# Mail functions
def sendMail(message):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    message['From'] = myEmailId

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(myEmailId, myEmailPassword)

        server.send_message(message)
        server.quit()

    except Exception as e:
        # Print any error messages to stdout
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to send OTP.")
