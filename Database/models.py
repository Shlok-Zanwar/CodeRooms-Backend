from sqlalchemy import Column, Integer, String, JSON, BIGINT, ForeignKey, DateTime, Boolean
from Database.database import Base
import datetime


# Login ---- sign-up Check
class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    otp = Column(String)
    isVerified = Column(Boolean, nullable=False, default=False)
    _try = Column(Integer, nullable=False, default=0)


class Room(Base):
    __tablename__ = 'Rooms'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("Users.id"), nullable=False)

