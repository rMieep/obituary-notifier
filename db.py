from abc import ABC, abstractmethod
from datetime import date

from sqlalchemy.orm import Session

from models import Obituary


class ObituaryRepository(ABC):
    @abstractmethod
    def add(self, obituary: Obituary):
        raise NotImplementedError

    @abstractmethod
    def exists(self, obituary: Obituary) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete_expired(self):
        raise NotImplementedError


class ObituaryRepositoryImpl(ObituaryRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, obituary: Obituary):
        self._session.add(obituary)

    def exists(self, obituary: Obituary) -> bool:
        return self._session.query(Obituary.link, Obituary.undertaker)\
            .filter(Obituary.link == obituary.link)\
            .filter(Obituary.undertaker == obituary.undertaker)\
            .first() is not None

    def delete_expired(self):
        today = date.today()
        self._session.query(Obituary).filter(Obituary.expiration_date < today).delete()
