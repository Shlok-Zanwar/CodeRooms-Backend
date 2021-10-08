from sqlalchemy import Column, Integer, String, JSON, BIGINT, ForeignKey, DateTime, Boolean
from Database.database import Base
from datetime import datetime


# Login ---- sign-up Check
class Users(Base):
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
    createdAt = Column(DateTime)
    verifiedAt = Column(DateTime)

class Rooms(Base):
    __tablename__ = 'Rooms'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    ownerId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    name = Column(String)
    enrolled = Column(Integer, nullable=False, default=0)
    waitingRoomEnabled = Column(Boolean, nullable=False, default=False)
    visibility = Column(String, nullable=False, default="private") # public/private/hidden
    createdAt = Column(DateTime, default=datetime.now())

    specialFields = Column(JSON)
    # specialFields = [
    #     {
    #         "field": "Name",
    #     },
    #     {
    #         "field": "Gr No."
    #     }
    # ]


class RoomMembers(Base):
    __tablename__ = 'RoomMembers'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    roomId = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    joinedAt = Column(DateTime)
    specialFields = Column(JSON)


class WaitingRoom(Base):
    __tablename__ = 'WaitingRoom'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    roomId = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    joinedAt = Column(DateTime)
    specialFields = Column(JSON)


class Questions(Base):
    __tablename__ = 'Questions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    roomId = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    createdBy = Column(Integer, ForeignKey("Users.id"), nullable=False)

    createdAt = Column(DateTime)
    endTime = Column(DateTime)
    isVisible = Column(Boolean, nullable=False, default=True)

    _type = Column(String)                          # Code, eg:-form .....

    title = Column(String, nullable=False)
    template = Column(JSON, nullable=False)
    testCases = Column(JSON)
    noOfTestCases = Column(Integer)
    submissionCountAllowed = Column(Integer) #no of submissions allowed

class Submissions(Base):
    __tablename__ = 'Submissions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    code = Column(String)
    testCasesPassed = Column(Integer)
    submittedAt = Column(DateTime)

