import json

from flask import Flask, request, jsonify
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker

from models import Meeting, ParticipantEmails, engine
from pydantic_validation import MeetingSchema

app = Flask(__name__)
Session = sessionmaker(bind=engine)
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


def make_pydantic_error_message(e):
    """Функция формирования сообщения об ошибке валидации входных данных"""
    error_message = ''
    for error in json.loads(e.json()):
        error_message += f'{error["msg"]} at {",".join(error["loc"])};'
    return error_message


@app.route('/api/meeting/create', methods=['POST'])
def meeting_create():
    """Создание встречи"""
    session = Session()

    # Валидация входных данных
    if request.json is None:
        return jsonify({'ok': False, 'error': 'json is missing'})

    try:
        meeting_validated = MeetingSchema(**request.json)
    except ValidationError as e:
        error_message = make_pydantic_error_message(e)
        return jsonify({'ok': False, 'error': error_message})

    new_meeting = Meeting(title=meeting_validated.title,
                          start_date_time=meeting_validated.start_date_time,
                          end_date_time=meeting_validated.end_date_time)
    session.add(new_meeting)
    session.commit()

    for email in meeting_validated.participant_emails:
        new_email = ParticipantEmails(meeting_id=new_meeting.id,
                                      email=email)
        session.add(new_email)

    session.commit()

    return jsonify({'ok': True, 'created_id': new_meeting.id})


@app.route('/api/meeting/edit/<meeting_id>', methods=['PATCH'])
def meeting_edit(meeting_id):
    """Редактирование встречи по id"""
    session = Session()

    # Валидация входных данных
    if request.json is None:
        return jsonify({'ok': False, 'error': 'json is missing'})

    try:
        meeting_validated = MeetingSchema(**request.json)
    except ValidationError as e:
        error_message = make_pydantic_error_message(e)
        return jsonify({'ok': False, 'error': error_message})

    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        return jsonify({'ok': False, 'error': f'Meeting with id {meeting_id} does not exists'})

    meeting.title = meeting_validated.title
    meeting.start_date_time = meeting_validated.start_date_time
    meeting.end_date_time = meeting_validated.end_date_time

    emails = session.query(ParticipantEmails).filter_by(meeting_id=meeting.id)
    for email in emails:
        session.delete(email)

    for email in meeting_validated.participant_emails:
        new_email = ParticipantEmails(meeting_id=meeting.id,
                                      email=email)
        session.add(new_email)
    session.commit()

    return jsonify({'ok': True, 'edited_id': meeting.id})


@app.route('/api/meeting/delete/<meeting_id>', methods=['DELETE'])
def meeting_delete(meeting_id):
    """Удаление встречи по id"""
    session = Session()

    meeting = session.get(Meeting, meeting_id)

    # Валидация входных данных
    if meeting is None:
        return jsonify({'ok': False, 'error': f'Meeting with id {meeting_id} does not exists'})

    session.delete(meeting)
    session.commit()

    return jsonify({'ok': True})


@app.route('/api/meeting/get/<meeting_id>', methods=['GET'])
def meeting_get(meeting_id):
    """Получение встречи по id"""
    session = Session()

    meeting = session.get(Meeting, meeting_id)

    # Валидация входных данных
    if meeting is None:
        return jsonify({'ok': False, 'error': f'Meeting with id {meeting_id} does not exists'})

    return jsonify(meeting.as_dict())


@app.route('/api/meetings/get', methods=['GET'])
def meetings_get_all():
    """Получение всех встреч"""
    session = Session()

    # Получение номера страницы
    page = request.args.get('page')
    if page is None:
        page = 0
    page = int(page)

    # Получение кол-ва встреч на странице
    # Если кол-во больше, чем MAX_PAGE_SIZE, то присваиваем MAX_PAGE_SIZE
    page_size = request.args.get('page_size')
    if page_size is None:
        page_size = DEFAULT_PAGE_SIZE
    page_size = int(page_size)

    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE

    meetings = session.query(Meeting).slice(page * page_size, (page + 1) * page_size)
    meetings_count = session.query(Meeting).count()

    has_next_page = True if (page + 1) * page_size < meetings_count else False

    return jsonify({'meetings': [m.as_dict() for m in meetings],
                    'has_next_page': has_next_page,
                    'page_size': page_size,
                    'page': page})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
