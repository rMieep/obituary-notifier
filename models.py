from datetime import date

from sqlalchemy import Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Obituary(Base):
    __tablename__ = "obituary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    date_of_death = Column(Date)
    expiration_date = Column(Date)
    undertaker = Column(String(20))
    link = Column(String)
    image_link = Column(String)

    def __init__(self, name: str, date_of_death: date, expiration_date: date, undertaker: str, link: str,
                 image_link: str):
        self.name = name
        self.date_of_death = date_of_death
        self.expiration_date = expiration_date
        self.undertaker = undertaker
        self.link = link
        self.image_link = image_link

    def __repr__(self):
        return f"<Obituary(Name={self.name}, Date of Death={self.date_of_death}, Undertaker={self.undertaker})>"

