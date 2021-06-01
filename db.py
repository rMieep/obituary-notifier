from abc import ABCMeta, abstractmethod
from datetime import timedelta, date

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from models import Base, Obituary


class ObituaryDB:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, obituary: Obituary) -> Obituary:
        raise NotImplemented

    @abstractmethod
    def exists(self, obituary: Obituary) -> bool:
        raise NotImplemented

    @abstractmethod
    def clean_up_expired(self):
        raise NotImplemented


class SQLiteObituaryDB(ObituaryDB):

    def __init__(self, path_to_db: str = 'obituary.db'):
        engine = create_engine('sqlite:///' + path_to_db)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.__session = Session()

    def add(self, obituary: Obituary):
        self.__session.add(obituary)

    def exists(self, obituary: Obituary) -> bool:
        return self.__session.query(Obituary).filter(and_(
            Obituary.id == obituary.identifier,
            Obituary.undertaker == obituary.undertaker_identifier
        )).exists()

    def clean_up_expired(self):
        self.__session.query(Obituary).delete().where(Obituary.expiration_date < date.today())


