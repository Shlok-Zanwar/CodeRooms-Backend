from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from Database.database import Base
from datetime import datetime


# Login ---- sign-up Check
class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    otp = Column(String)
    isVerified = Column(Boolean, nullable=False, default=False)
    _try = Column(Integer, nullable=False, default=0)
    createdAt = Column(DateTime)
    verifiedAt = Column(DateTime)
    accountType = Column(Integer)


class Rooms(Base):
    __tablename__ = 'Rooms'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    ownerId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    name = Column(String)
    # enrolled = Column(Integer, nullable=False, default=0)
    waitingRoomEnabled = Column(Boolean, nullable=False, default=False)
    visibility = Column(String, nullable=False, default="private") # public/private/hidden
    createdAt = Column(DateTime, default=datetime.now())

    specialFields = Column(String)


class RoomMembers(Base):
    __tablename__ = 'RoomMembers'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    roomId = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    joinedAt = Column(DateTime)
    specialFields = Column(String)
    inWaitingRoom = Column(Boolean, nullable=False)
    isRejected = Column(Boolean, nullable=False)


class Questions(Base):
    __tablename__ = 'Questions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    roomId = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    createdBy = Column(Integer, ForeignKey("Users.id"), nullable=False)

    createdAt = Column(DateTime)
    endTime = Column(DateTime)
    isVisible = Column(Boolean, nullable=False, default=True)

    _type = Column(String)                          # Code, eg:-form .....

    title = Column(String, nullable=False, default="Title")
    template = Column(String)
    testCases = Column(String)
    submissionCountAllowed = Column(Integer) #no of submissions allowed


class FileSubmissions(Base):
    __tablename__ = 'FileSubmissions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    fileName = Column(String, nullable=False, default="File")
    submittedAt = Column(DateTime)

class CodeSubmissions(Base):
    __tablename__ = 'CodeSubmissions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    code = Column(String)
    testCasesPassed = Column(Integer)
    language = Column(String)
    submittedAt = Column(DateTime)


class SavedCodes(Base):
    __tablename__ = 'SavedCodes'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    code = Column(String)
    language = Column(String)
    savedAt = Column(DateTime)


