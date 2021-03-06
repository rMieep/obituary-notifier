from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import ObituaryRepositoryImpl, ObituaryRepository
from models import Base
from notifier import Notifier, EMailNotifier, GMailClient
from undertaker import Undertaker, UndertakerImpl

engine = create_engine('sqlite:///obituary.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def main():
    keywords = create_keywords()
    undertakers = create_undertakers()
    notifiers = create_notifier()

    with Session() as session, session.begin():
        repo = create_obituary_repository(session)
        for undertaker in undertakers:
            obituaries = undertaker.get_obituaries()

            for obituary in obituaries:
                if not repo.exists(obituary):
                    repo.add(obituary)
                    description = undertaker.get_description(obituary)
                    if any(word in description for word in keywords):
                        for notifier in notifiers:
                            notifier.notify(obituary)

        repo.delete_expired()


def create_keywords() -> List[str]:
    return ["Elsdorf", "Bockhorst", "Badenhorst", "Wistedt"]


def create_undertakers() -> List[Undertaker]:
    return [UndertakerImpl(identifier='oehrding', base_url='https://oerding.gemeinsam-trauern.net'),
            UndertakerImpl(identifier='bahrenburg', base_url='https://gemeinsam-trauern.bahrenburg-bestattungen.de')]


def create_notifier() -> List[Notifier]:
    return [EMailNotifier(GMailClient(
        sender_address="sender_address",
        receiver_addresses=["receiver_address"]
    ))]


def create_obituary_repository(curr_session: Session) -> ObituaryRepository:
    return ObituaryRepositoryImpl(curr_session)


if __name__ == '__main__':
    main()
