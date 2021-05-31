from sqlalchemy import Column, Integer, String
from database import Base


class Words(Base):
    __tablename__ = 'Words'
    id = Column(Integer, primary_key=True)
    enc = Column(String)
    result = Column(String)
