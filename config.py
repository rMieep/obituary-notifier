from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from yaml import load


class NotifierConfig(ABC):
    pass


@dataclass
class EmailNotifierConfig(NotifierConfig):

    __server_address: str
    __server_port: int
    __sender_address: str
    __sender_password: str
    __receiver_addresses: List[str]

    @property
    def server_address(self) -> str:
        return self.__server_address

    @server_address.setter
    def server_address(self, value) -> None:
        self.__server_address = value

    @property
    def server_port(self) -> int:
        return self.__server_port

    @server_port.setter
    def server_port(self, value) -> None:
        self.__server_port = value

    @property
    def sender_address(self) -> str:
        return self.__sender_address

    @sender_address.setter
    def sender_address(self, value) -> None:
        self.__sender_address = value

    @property
    def sender_password(self) -> str:
        return self.__sender_password

    @sender_password.setter
    def sender_password(self, value) -> None:
        self.__sender_password = value

    @property
    def receiver_addresses(self) -> List[str]:
        return self.__receiver_addresses

    @receiver_addresses.setter
    def receiver_addresses(self, value) -> None:
        self.__receiver_addresses = value


class KeywordsConfig(ABC):
    pass


@dataclass
class DefaultKeywordsConfig(KeywordsConfig):

    __keywords: List[str]

    @property
    def keywords(self) -> List[str]:
        return self.__keywords

    @keywords.setter
    def keywords(self, value: List[str]) -> None:
        self.__keywords = value


class UndertakerConfig(ABC):
    pass


@dataclass
class DefaultUndertakerConfig(UndertakerConfig):

    __identifier: str
    __base_url: str

    @property
    def identifier(self) -> str:
        return self.__identifier

    @identifier.setter
    def identifier(self, value: str) -> None:
        self.__identifier = value

    @property
    def base_url(self) -> str:
        return self.__base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        self.__base_url = value


class UndertakersConfig(ABC):
    pass


@dataclass
class DefaultUndertakersConfig(UndertakersConfig):

    __undertakers: List[DefaultUndertakerConfig]

    @property
    def undertakers(self) -> List[DefaultUndertakerConfig]:
        return self.__undertakers

    @undertakers.setter
    def undertakers(self, value: List[DefaultUndertakerConfig]):
        self.__undertakers = value


class Config(ABC):

    @property
    @abstractmethod
    def notifier_config(self) -> NotifierConfig:
        raise NotImplemented

    @property
    @abstractmethod
    def keywords_config(self) -> KeywordsConfig:
        raise NotImplemented

    @property
    @abstractmethod
    def undertakers_config(self) -> UndertakersConfig:
        raise NotImplemented


@dataclass
class DefaultConfig(Config):

    __notifier_config: EmailNotifierConfig
    __keywords_config: DefaultKeywordsConfig
    __undertakers_config: DefaultUndertakerConfig

    @property
    def notifier_config(self) -> EmailNotifierConfig:
        return self.__notifier_config

    @notifier_config.setter
    def notifier_config(self, value: EmailNotifierConfig) -> None:
        self.__notifier_config = value

    @property
    def keywords_config(self) -> DefaultKeywordsConfig:
        return self.__keywords_config

    @keywords_config.setter
    def keywords_config(self, value: DefaultKeywordsConfig) -> None:
        self.__keywords_config = value

    @property
    def undertakers_config(self) -> DefaultUndertakerConfig:
        return self.__undertakers_config

    @undertakers_config.setter
    def undertakers_config(self, value: DefaultUndertakerConfig) -> None:
        self.__undertakers_config = value


class NotifierConfigLoader(ABC):

    @abstractmethod
    def load(self, config: dict) -> NotifierConfig:
        raise NotImplemented


class EmailConfigLoader(NotifierConfigLoader):

    def load(self, config: dict) -> EmailNotifierConfig:
        return EmailNotifierConfig(
            config['server_address'],
            config['server_port'],
            config['sender_address'],
            config['sender_password'],
            config['receiver_addresses']
        )


class KeywordsConfigLoader(ABC):

    @abstractmethod
    def load(self, config: list) -> KeywordsConfig:
        raise NotImplemented


class DefaultKeywordsConfigLoader(KeywordsConfigLoader):

    def load(self, config: list) -> DefaultKeywordsConfig:
        return DefaultKeywordsConfig(
            config
        )


class UndertakerConfigLoader(ABC):

    @abstractmethod
    def load(self, config: dict) -> UndertakerConfig:
        raise NotImplemented


class DefaultUndertakerConfigLoader(UndertakerConfigLoader):

    def load(self, config: dict) -> DefaultUndertakerConfig:
        return DefaultUndertakerConfig(
            config['identifier'],
            config['base_url']
        )


class UndertakersConfigLoader(ABC):

    @abstractmethod
    def load(self, config: list) -> UndertakersConfig:
        raise NotImplemented


class DefaultUndertakersConfigLoader(UndertakersConfigLoader):

    def __init__(self, undertaker_config_loader: DefaultUndertakerConfigLoader):
        self.__undertaker_config_loader = undertaker_config_loader

    def load(self, config: list) -> DefaultUndertakersConfig:
        undertakers = list()
        for undertaker in config:
            undertakers.append(self.__undertaker_config_loader.load(undertaker))

        return DefaultUndertakersConfig(undertakers)


class ConfigLoader(ABC):
    _config: Config = None

    @property
    def config(self) -> Config:
        if ConfigLoader._config is None:
            self._load()
        return ConfigLoader._config

    @abstractmethod
    def _load(self) -> None:
        raise NotImplemented


class DefaultConfigLoader(ConfigLoader):

    def __init__(self, uri: str,
                 notifier_config_loader: EmailConfigLoader,
                 keywords_config_loader: DefaultKeywordsConfigLoader,
                 undertaker_config_loader: DefaultUndertakersConfigLoader) -> None:

        super().__init__()
        self.__notifier_config_loader = notifier_config_loader
        self.__keywords_config_loader = keywords_config_loader
        self.__undertaker_config_loader = undertaker_config_loader
        self.__uri = uri

    def _load(self) -> None:
        with open(self.__uri, 'r') as stream:
            config = load(stream)
            ConfigLoader._config = DefaultConfig(
                self.__notifier_config_loader.load(config['notifier']),
                self.__keywords_config_loader.load(config['keywords']),
                self.__undertaker_config_loader.load(config['undertakers'])
            )


class ConfigLoaderFactory(ABC):

    @abstractmethod
    def create(self, uri: str) -> ConfigLoader:
        raise NotImplemented


class DefaultConfigLoaderFactory(ConfigLoaderFactory):

    def create(self, uri: str) -> DefaultConfigLoader:
        return DefaultConfigLoader(
            uri,
            EmailConfigLoader(),
            DefaultKeywordsConfigLoader(),
            DefaultUndertakersConfigLoader(DefaultUndertakerConfigLoader())
        )
