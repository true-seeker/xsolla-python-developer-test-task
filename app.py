import json
from datetime import datetime

from flask import Flask, request, jsonify
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker

from models import Meeting, ParticipantEmails, engine
from pydantic_validation import MeetingSchema

app = Flask(__name__)
Session = sessionmaker(bind=engine)
DEFAULT_PAGE_SIZE = 50
request_json = json.load(open('test.json'))
request_json2 = json.load(open('test2.json'))
request_json3 = json.load(open('test3.json'))


def make_pydantic_error_message(e):
    error_message = ''
    for error in json.loads(e.json()):
        error_message += f'{error["msg"]} at {",".join(error["loc"])};'
    return error_message


def reformat_datetime(dt):
    try:
        reformatted_datetime = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None  # TODO
    return reformatted_datetime


@app.route('/api/meeting/create', methods=['GET', 'POST'])  # TODO remove get
def meeting_create():
    session = Session()

    print(request.json)
    if request_json.get('meeting') is None:
        return jsonify({'ok': False, 'error': '"meeting" key is missing'})

    try:
        meeting_validated = MeetingSchema(**request_json['meeting'])
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

    print(new_meeting)

    return jsonify({'ok': True, 'created_id': new_meeting.id})


@app.route('/api/meeting/edit', methods=['GET', 'PATCH'])  # TODO remove get
def meeting_edit():
    session = Session()

    print(request.json)
    new_meeting_json = request_json2['meeting']  # TODO request json

    meeting = session.get(Meeting, new_meeting_json['id'])  # TODO if None

    meeting.title = new_meeting_json['title']
    meeting.start_date_time = reformat_datetime(new_meeting_json['start_date_time'])
    meeting.end_date_time = reformat_datetime(new_meeting_json['end_date_time'])

    emails = session.query(ParticipantEmails).filter_by(meeting_id=meeting.id)
    for email in emails:
        session.delete(email)

    for email in new_meeting_json['participant_emails']:
        new_email = ParticipantEmails(meeting_id=new_meeting_json['id'],
                                      email=email)
        session.add(new_email)
    session.commit()

    print(meeting)

    return jsonify({'ok': True, 'edited_id': meeting.id})


@app.route('/api/meeting/delete', methods=['GET', 'DELETE'])  # TODO remove get
def meeting_delete():
    session = Session()

    print(request.json)
    meeting_json = request_json2['meeting']  # TODO request json
    meeting = session.get(Meeting, meeting_json['id'])  # TODO if None

    session.delete(meeting)
    session.commit()

    return jsonify({'ok': True})


@app.route('/api/meeting/get', methods=['GET'])
def meeting_get():
    session = Session()

    print(request.json)
    meeting_json = request_json3['meeting']  # TODO request json
    meeting = session.get(Meeting, meeting_json['id'])  # TODO if None

    return jsonify(meeting.as_dict())


@app.route('/api/meetings/get', methods=['GET'])
def meetings_get_all():
    session = Session()

    print(request.json)

    page = 0  # TODO remove
    meetings = session.query(Meeting).slice(page * DEFAULT_PAGE_SIZE, (page + 1) * DEFAULT_PAGE_SIZE)
    meetings_count = session.query(Meeting).count()

    has_next_page = True if (page + 1) * DEFAULT_PAGE_SIZE < meetings_count else False

    return jsonify({'meetings': [m.as_dict() for m in meetings],
                    'has_next_page': has_next_page,
                    'page_size': DEFAULT_PAGE_SIZE})


if __name__ == '__main__':
    app.run()
