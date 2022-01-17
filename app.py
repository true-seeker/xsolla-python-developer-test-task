from flask import Flask, request, jsonify
from models import Meeting, ParticipantEmails, engine
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
Session = sessionmaker(bind=engine)

request_json = json.load(open('test.json'))
request_json2 = json.load(open('test2.json'))


def reformat_datetime(dt):
    try:
        reformatted_datetime = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None  # TODO
    return reformatted_datetime


# TODO pydantic
@app.route('/api/meetings/create', methods=['GET', 'POST'])  # TODO remove get
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


@app.route('/api/meetings/edit', methods=['GET', 'POST'])
def meeting_edit():
    session = Session()

    print(request.json)
    new_meeting_json = request_json2['meeting']  # TODO request json

    meeting = session.query(Meeting).filter_by(id=new_meeting_json['id']).first()

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


if __name__ == '__main__':
    app.run()
