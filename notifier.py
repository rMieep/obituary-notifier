from smtplib import SMTP
from abc import ABCMeta, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EMailManager:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        raise NotImplemented

    @abstractmethod
    def __enter__(self):
        raise NotImplemented

    @abstractmethod
    def send(self, receiver_address: str, subject: str, message: str):
        raise NotImplemented

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplemented


class TLSEMailManager(EMailManager):

    def __init__(self, server_uri, server_port, sender_address, sender_pass):
        self.__server_uri = server_uri
        self.__server_port = server_port
        self.__sender_address = sender_address
        self.__sender_pass = sender_pass

    def __enter__(self):
        self.__session = SMTP(self.__server_uri, self.__server_port)  # FIXME pull out
        self.__session.starttls()
        self.__session.login(self.__sender_address, self.__sender_pass)

    def send(self, receiver_address: str, subject: str, content: str):  # FIXME pull out
        message = MIMEMultipart()
        message['From'] = self.__sender_address
        message['To'] = receiver_address
        message['Subject'] = subject
        message.attach(MIMEText(content, 'plain'))

        mail = message.as_string()

        self.__session.sendmail(self.__sender_address, receiver_address, mail)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.quit()


class Notifier:
    __metaclass__ = ABCMeta

    @abstractmethod
    def notify(self, title: str, message: str):
        raise NotImplemented


class EMailNotifier(Notifier):
    def __init__(self, email_manager: EMailManager) -> None:
        self.__email_manager = email_manager

    def notify(self, title: str, content: str):
        subject = self.__build_subject()
        content = self.__build_content()
        with self.__email_manager as manager:
            manager.send('', subject, content)

    def __build_subject(self):
        pass

    def __build_content(self):
        pass
