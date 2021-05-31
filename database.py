from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import environ

SQLALCHEMY_DATABASE_URL = environ['DATABASE_URL'].replace('postgres', 'postgresql')

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Session = sessionmaker()
Session.configure(bind=engine)

Base = declarative_base()