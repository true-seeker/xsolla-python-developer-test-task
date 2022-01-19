from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Таблица встреч
class Meeting(Base):
    __tablename__ = 'meetings'

    def as_dict(self):
        meeting_dict = {'id': self.id,
                        'title': self.title,
                        'start_date_time': self.start_date_time.strftime(
                            '%Y-%m-%dT%H:%M:%S') if self.start_date_time is not None else '',
                        'end_date_time': self.end_date_time.strftime(
                            '%Y-%m-%dT%H:%M:%S') if self.end_date_time is not None else '',
                        'emails': []}

        for email in self.emails:
            meeting_dict['emails'].append({'email': email.email, 'id': email.id})

        return meeting_dict

    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    start_date_time = Column(DateTime)
    end_date_time = Column(DateTime)
    emails = relationship("ParticipantEmails", back_populates='meeting', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f'{self.id}|{self.title}|{self.start_date_time}|{self.end_date_time}'


# Таблица с email участников встреч
class ParticipantEmails(Base):
    __tablename__ = 'participant_emails'
    id = Column(Integer, primary_key=True)
    meeting_id = Column(ForeignKey('meetings.id'))
    meeting = relationship("Meeting", back_populates="emails")
    email = Column(String(128))

    def __repr__(self):
        return f'{self.id}|{self.meeting_id}|{self.email}'


engine = create_engine('sqlite:///sqlite3.db')

if __name__ == '__main__':
    # Инициализация таблиц в БД
    Base.metadata.create_all(engine)
