import os
from base64 import urlsafe_b64encode
from smtplib import SMTP
from abc import abstractmethod, ABC
from email.mime.text import MIMEText
from typing import List

from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from models import Obituary


class EMailClient(ABC):
    """Abstract EMailClient that allows to send emails"""

    def __init__(self, sender_address: str):
        self._sender_address = sender_address

    @abstractmethod
    def __enter__(self):
        raise NotImplemented

    @abstractmethod
    def send(self, subject: str, message: str):
        raise NotImplemented

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplemented

    def _build_mail(self, receiver_address: str, subject: str, content: str):
        message = MIMEText(content, "plain")
        message['from'] = self._sender_address
        message['to'] = receiver_address
        message['subject'] = subject

        return message


class GMailClient(EMailClient):
    """Concrete EMailClient that uses the GMail API to send emails"""
    def __init__(self, sender_address: str, receiver_addresses: List[str], credentials_path: str = "credentials.json"):
        super(GMailClient, self).__init__(sender_address)
        self._receiver_addresses = receiver_addresses
        self._credentials = None
        self._SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self._credentials_path = credentials_path

    def __enter__(self):
        if os.path.exists('token.json'):
            self._credentials = Credentials.from_authorized_user_file('token.json', self._SCOPES)

        if not self._credentials or not self._credentials.valid:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._credentials_path, self._SCOPES)
                self._credentials = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self._credentials.to_json())

        self._service = build('gmail', 'v1', credentials=self._credentials)

    def _build_mail(self, receiver_address: str, subject: str, content: str):
        message = super(GMailClient, self)._build_mail(receiver_address, subject, content)
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    def send(self, subject: str, content: str):
        for receiver_address in self._receiver_addresses:
            try:
                self._service.users().messages().send(userId="me", body=self._build_mail(
                    receiver_address, subject, content)).execute()
            except errors.HttpError as error:
                print('An error occurred: %s' % error)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._service.close()


class SMTPEMailClient(EMailClient):
    """Concrete EMailClient that uses SMTP to send emails"""
    def __init__(self, server_address: str, server_port: int, sender_address: str, sender_password: str,
                 receiver_addresses: List[str]):
        super(SMTPEMailClient, self).__init__(sender_address)

        self._server_address = server_address
        self._server_port = server_port
        self._sender_pass = sender_password
        self._receiver_addresses = receiver_addresses

    def __enter__(self):
        self._session = SMTP(self._server_address, self._server_port)
        self._session.starttls()
        self._session.login(self._sender_address, self._sender_pass)

    def _build_mail(self, receiver_address: str, subject: str, content: str):
        return super(SMTPEMailClient, self)._build_mail(receiver_address, subject, content).as_string()

    def send(self, subject: str, content: str):
        for receiver_address in self._receiver_addresses:
            self._session.sendmail(
                from_addr=self._sender_address,
                to_addrs=receiver_address,
                msg=self._build_mail(receiver_address, subject, content)
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.quit()


class Notifier(ABC):
    """ Abstract Notifier that notifies external users about an obituary"""
    @abstractmethod
    def notify(self, obituary: Obituary):
        raise NotImplemented


class EMailNotifier(Notifier):
    """Concrete notifier that notifies external users via email"""
    def __init__(self, email_client: EMailClient):
        self._client = email_client

    def notify(self, obituary: Obituary):
        with self._client:
            self._client.send(self._build_subject(obituary), self._build_content(obituary))

    @staticmethod
    def _build_subject(obituary: Obituary):
        return "Nachruf: " + obituary.name

    @staticmethod
    def _build_content(obituary: Obituary):
        return f"Name: {obituary.name}\n" \
               f"Todestag: {obituary.date_of_death.strftime('%d.%m.%Y')}\n" \
               f"Link zur Internetseite: {obituary.link}\n" \
               f"Link zum Bild: {obituary.image_link}"
