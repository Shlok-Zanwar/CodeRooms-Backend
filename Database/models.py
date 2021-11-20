from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from Database.database import Base
from datetime import datetime


# Login ---- sign-up Check
class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String(750), unique=True)
    fname = Column(String(750))
    lname = Column(String(750))
    email = Column(String(750), unique=True, nullable=False)
    password = Column(String(750), nullable=False)
    otp = Column(String(750))
    isVerified = Column(Boolean, nullable=False, default=False)
    _try = Column(Integer, nullable=False, default=0)
    createdAt = Column(DateTime)
    verifiedAt = Column(DateTime)
    accountType = Column(Integer)


class Rooms(Base):
    __tablename__ = 'Rooms'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    ownerId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    name = Column(String(750))
    # enrolled = Column(Integer, nullable=False, default=0)
    waitingRoomEnabled = Column(Boolean, nullable=False, default=False)
    visibility = Column(String(750), nullable=False, default="private") # public/private/hidden
    createdAt = Column(DateTime, default=datetime.now())

    specialFields = Column(String(750))


class RoomMembers(Base):
    __tablename__ = 'RoomMembers'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    roomId = Column(Integer, ForeignKey("Rooms.id"), nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    joinedAt = Column(DateTime)
    specialFields = Column(String(750))
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

    _type = Column(String(750))                          # Code, eg:-form .....

    title = Column(String(750), nullable=False, default="Title")
    template = Column(String(50000))
    testCases = Column(String(750))
    submissionCountAllowed = Column(Integer) #no of submissions allowed


class FileSubmissions(Base):
    __tablename__ = 'FileSubmissions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    fileName = Column(String(750), nullable=False, default="File")
    submittedAt = Column(DateTime)

class CodeSubmissions(Base):
    __tablename__ = 'CodeSubmissions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    code = Column(String(1000))
    testCasesPassed = Column(Integer)
    language = Column(String(750))
    submittedAt = Column(DateTime)


class SavedCodes(Base):
    __tablename__ = 'SavedCodes'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    questionId = Column(Integer, ForeignKey("Questions.id"), nullable=False)
    code = Column(String(750))
    language = Column(String(750))
    savedAt = Column(DateTime)


