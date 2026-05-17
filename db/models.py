from sqlalchemy import Column, Integer, String, Text
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    type = Column(String)
    data = Column(Text)