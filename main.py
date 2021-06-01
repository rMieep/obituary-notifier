from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

import requests
import locale
import pytesseract

from datetime import datetime, date, timedelta

from PIL import Image
from sqlalchemy import Column, String, Date, create_engine, and_
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def exists(session, obituary):
    return bool(session.query(Obituary).filter(and_(Obituary.id == obituary.id, Obituary.undertaker == obituary.undertaker)).first())


if __name__ == '__main__':
    engine = create_engine('sqlite:///obituary.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    db_session = Session()

    for undertaker in undertakers:
        response = requests.get(undertaker['base_url'] + '/json/OrdersPage?nr=1&size=20')
        data = []
        if response.ok:
            data = response.json()['orders']

        obituaries = []

        for item in data:
            obituary_identifier = item['relativeUri'].split('/')[2]
            locale.setlocale(locale.LC_TIME, '')
            date_of_death = datetime.strptime(item['dateOfDeath'], '%d. %B %Y').date()

            obituaries.append(Obituary(
                id=obituary_identifier,
                name=item['fullName'],
                expiration_date=date_of_death + timedelta(days=14),
                undertaker=undertaker['identifier']
            ))

        obituaries = list(filter(lambda obituary: obituary.expiration_date > date.today(), obituaries))

        for obituary in obituaries:
            if not exists(db_session, obituary):
                db_session.add(obituary)
                info = pytesseract.image_to_string(
                    Image.open(requests.get(
                        undertaker['base_url'] + '/Begleiten/' + obituary.id + "/Profilbild", stream=True).raw),
                    lang='deu'
                )
                if any(word in info for word in keywords):
                    email_session = SMTP(email_server_address, email_server_port)
                    email_session.starttls()
                    email_session.login(email_sender_address, email_sender_pass)

                    message = MIMEMultipart()
                    message['From'] = email_sender_address
                    message['To'] = email_receiver_address
                    message['Subject'] = 'Nachruf ' + obituary.name
                    message.attach(MIMEText(undertaker['base_url'] + '/Begleiten/' + obituary.id, 'plain'))

                    mail = message.as_string()
                    email_session.sendmail(email_sender_address, email_receiver_address, mail)

                    email_session.quit()

    db_session.query(Obituary).filter(Obituary.expiration_date < date.today()).delete()
    db_session.commit()
    db_session.close()
