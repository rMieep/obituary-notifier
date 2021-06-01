import locale
from abc import ABC, abstractmethod
from datetime import date, timedelta, datetime
from typing import List

import requests
from PIL.Image import Image
from pytesseract import pytesseract

from models import Obituary


class Undertaker(ABC):

    @abstractmethod
    def get_info(self, obituary: Obituary) -> str:
        raise NotImplemented

    @abstractmethod
    def get_obituaries(self) -> List[Obituary]:
        raise NotImplemented


class UndertakerImp(Undertaker):

    def __init__(self, identifier: str, base_url: str, max_age: int):
        self.identifier = identifier
        self.base_url = base_url
        self.max_age = max_age

    def get_info(self, obituary: Obituary) -> str:
        return get_text_from_image(get_image_from_url(self.__build_image_uri(obituary)))

    def get_obituaries(self) -> List[Obituary]:
        return self.__filter_obituaries(self.__convert_obituaries(self.__fetch_obituaries()))

    def __build_image_uri(self, obituary: Obituary) -> str:
        return self.base_url + '/Begleiten/' + obituary.identifier + "/Profilbild"

    def __fetch_obituaries(self) -> List:
        response = requests.get(self.base_url + '/json/OrdersPage?nr=1&size=20')
        if response.ok:
            return response.json()['orders']

    def __convert_obituaries(self, obituaries: List) -> List[Obituary]:
        converted_obituaries = []

        for obituary in obituaries:
            obituary_identifier = obituary['relativeUri'].split('/')[2]
            locale.setlocale(locale.LC_TIME, '')
            date_of_death = datetime.strptime(obituary['dateOfDeath'], '%d. %B %Y').date()

            converted_obituaries.append(Obituary(
                obituary_identifier,
                obituary['fullName'],
                date_of_death + timedelta(days=7),
                self.identifier
            ))

        return converted_obituaries

    def __filter_obituaries(self, obituaries: List[Obituary]) -> List[Obituary]:
        max_age_date = date.today() - timedelta(days=self.max_age)
        return list(filter(lambda obituary: obituary.date_of_death >= max_age_date, obituaries))


def get_text_from_image(image: Image) -> str:
    return pytesseract.image_to_string(image, lang='deu')


def get_image_from_url(url: str) -> Image:
    return Image.open(requests.get(url, stream=True).raw)
