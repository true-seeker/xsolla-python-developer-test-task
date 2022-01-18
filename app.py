import json
from datetime import datetime

from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker

from models import Meeting, ParticipantEmails, engine

app = Flask(__name__)
Session = sessionmaker(bind=engine)
DEFAULT_PAGE_SIZE = 50
request_json = json.load(open('test.json'))
request_json2 = json.load(open('test2.json'))
request_json3 = json.load(open('test3.json'))


def reformat_datetime(dt):
    try:
        reformatted_datetime = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None  # TODO
    return reformatted_datetime


# TODO pydantic
@app.route('/api/meeting/create', methods=['GET', 'POST'])  # TODO remove get
def meeting_create():
    session = Session()

    print(request.json)
    new_meeting_json = request_json['meeting']  # TODO request json
    new_meeting = Meeting(title=new_meeting_json['title'],
                          start_date_time=reformat_datetime(new_meeting_json['start_date_time']),
                          end_date_time=reformat_datetime(new_meeting_json['end_date_time']))
    session.add(new_meeting)
    session.commit()

    for email in new_meeting_json['participant_emails']:
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
