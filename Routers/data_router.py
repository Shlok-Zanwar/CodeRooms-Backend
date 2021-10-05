from fastapi import APIRouter, Depends, Request, HTTPException, status
from Database import database, models
from sqlalchemy.orm import Session
from Functions import Token
from pydantic import BaseModel
from typing import  Optional, List


router = APIRouter(
    tags=['Data'],
    # prefix="/auth"
)

get_db = database.get_db

@router.get('/')
def getData(
        # request: Request
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        # print(request.headers['Authorization'])
        id = Token.getCurrentUser(request.headers['Authorization'])
        return id
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.")
