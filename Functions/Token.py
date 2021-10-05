from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status


SECRET_KEY = "ApnaSecretBhidu"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 500

def createAccessToken(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verifyJWTToken(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
        # id: int = payload.get("username")
        # if id is None:
        #     raise credentials_exception
        # # token_data = schemas.TokenData(email=email)
        # return id
    except JWTError:
        raise credentials_exception



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def getCurrentUser(data: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verifyJWTToken(data, credentials_exception)
    # print(payload)
    return payload