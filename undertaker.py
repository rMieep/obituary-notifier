import locale
from abc import ABC, abstractmethod
from datetime import date, timedelta, datetime
from typing import List, Dict

import requests
from PIL import Image
from pytesseract import pytesseract

from models import Obituary


class Undertaker(ABC):
    """ An abstract Undertaker class
    Used to fetch obituaries and their descriptions

    Args:
        identifier: An unique identifier for that undertaker
        base_url: The base url used to query its obituaries
        max_death_age_in_days: The number of days an obituary should be considered
    """

    def __init__(self, identifier: str, base_url: str, max_death_age_in_days: int = 14):
        self._identifier = identifier
        self._base_url = base_url
        self._max_death_age_in_days = max_death_age_in_days

    @abstractmethod
    def get_description(self, obituary: Obituary) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_obituaries(self) -> List[Obituary]:
        raise NotImplementedError


class UndertakerImpl(Undertaker):
    """ Concrete Undertaker used for local undertakers Oehrding and Bahrenburg.
    As both of them use the same backend only one Undertaker implementation is, as of now, needed.

    """
    def get_description(self, obituary: Obituary) -> str:
        return self._get_text_from_image(self._get_image_from_url(obituary.image_link))

    def get_obituaries(self) -> List[Obituary]:
        return self._filter_obituaries(self._parse_obituaries(self._fetch_obituaries()))

    def _fetch_obituaries(self) -> List[Dict]:
        response = requests.get(self._base_url + '/json/OrdersPage?nr=1&size=20')
        if response.ok:
            return response.json()['orders']

    def _parse_obituaries(self, obituaries: List[Dict]) -> List[Obituary]:
        parsed_obituaries = []

        for obituary in obituaries:
            locale.setlocale(locale.LC_TIME, '')
            date_of_death = datetime.strptime(obituary['dateOfDeath'], '%d. %B %Y').date()

            parsed_obituaries.append(Obituary(
                name=obituary['fullName'],
                date_of_death=date_of_death,
                expiration_date=date_of_death + timedelta(days=self._max_death_age_in_days),
                undertaker=self._identifier,
                link=self._base_url + obituary['relativeUri'],
                image_link=self._base_url + obituary['imageUri']
            ))

        return parsed_obituaries

    @staticmethod
    def _filter_obituaries(obituaries: List[Obituary]) -> List[Obituary]:
        today = date.today()
        return list(filter(lambda obituary: obituary.expiration_date >= today, obituaries))

    @staticmethod
    def _get_image_from_url(url: str) -> Image:
        return Image.open(requests.get(url, stream=True).raw)

    @staticmethod
    def _get_text_from_image(image: Image) -> str:
        return pytesseract.image_to_string(image, lang='deu')

