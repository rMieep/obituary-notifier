import dataclasses

from sqlalchemy import Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


@dataclasses.dataclass
class Obituary(Base):
    __tablename__ = "obituary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    date_of_death = Column(Date)
    expiration_date = Column(Date)
    undertaker = Column(String(20))
    link = Column(String)
    image_link = Column(String)
