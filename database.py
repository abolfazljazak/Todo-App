from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext import declarative


SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos-db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_some_thears': False})

SessionLocal = sessionmaker(autocommit=False, autoflash=False, bind=engine)

Base = declarative()
