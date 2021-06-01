from sqlalchemy import Index, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Obituary(Base):
    __tablename__ = "obituary"
    id = Column(String(30), primary_key=True)
    expiration_date = Column(Date)
    undertaker = Column(String(20), primary_key=True)
    __table_args__ = (Index('id_date_of_death_undertaker_index', "id", "date_of_death", "undertaker"),)
