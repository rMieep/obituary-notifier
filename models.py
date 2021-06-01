from sqlalchemy import Column, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Obituary(Base):
    __tablename__ = "obituary"
    id = Column(String(30), primary_key=True)
    name = Column(String(30))
    expiration_date = Column(Date)
    undertaker = Column(String(20), primary_key=True)
