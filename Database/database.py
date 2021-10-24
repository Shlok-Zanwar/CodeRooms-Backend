from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import getenv

# SQLALCHAMY_DATABASE_URL = 'postgresql://usertest:usertest222@127.0.0.1:5432/dbtest'
# SQLALCHAMY_DATABASE_URL = 'sqlite:///./coderooms.db'
SQLALCHAMY_DATABASE_URL = f'sqlite:///{getenv("db_path")}coderooms.db'


engine = create_engine(SQLALCHAMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False,)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
