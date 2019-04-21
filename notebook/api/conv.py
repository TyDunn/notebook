"""
Check-in API.

Ty Dunn <ty@tydunn.com>
"""
#/env/bin/python

import json
import flask
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from fuzzywuzzy import process
from apscheduler.schedulers.background import BackgroundScheduler
import notebook
from .credentials import ACCOUNT_SID, AUTH_TOKEN, ACCEPTABLE_USERS, USERNAME, FROM_NUM, TO_NUM

client = Client(ACCOUNT_SID, AUTH_TOKEN) # pylint: disable=invalid-name


def schedule():
    """
    Schedule check-ins using background scheduler.
    """
    start_check_in()
    sched = BackgroundScheduler()
    sched.add_job(start_check_in, 'interval', minutes=0.1)
    sched.start()


@notebook.app.route("/sms", methods=['GET', 'POST'])
def sms():
    """
    Process incoming messages, call check_in(), and send response.
    """
    number = flask.request.form['From']
    text = flask.request.form['Body']
    if text == 'start':
        schedule()
        resp = MessagingResponse()
        return str(resp)
    return str(do_check_in(number, text))


def get_step_id(username):
    """
    Determine what step a user is on currently.
    """
    sql = 'SELECT *, max(created) FROM check_ins WHERE username = ?'
    check_in = notebook.model.query_db(sql, (username,))[0]
    check_in_id = check_in['check_in_id']
    step = 1
    if check_in['emotion1']:
        step = 2
        if check_in['emotion2']:
            step = 3
            if check_in['emotion3']:
                step = 4
                if check_in['thoughts']:
                    step = 5
                    if check_in['tags']:
                        step = 6
    return step, check_in_id


def start_check_in():
    """
    Start a check in.
    """
    with notebook.app.app_context():
        sql = 'INSERT INTO check_ins(username) VALUES (?)'
        notebook.model.update_db(sql, (USERNAME,))
        core = ['love', 'joy', 'surprise', 'sadness', 'anger', 'fear']
        body = 'Please select the emotion that best describes how you felt:'
        for emotion in core:
            body += ' ' + emotion
        message = client.messages.create(body=body, from_=FROM_NUM, to=TO_NUM)
    # what is supposed to happen here?

def do_check_in(number, text):
    """
    Check in based on step.
    """
    resp = MessagingResponse()
    if number in ACCEPTABLE_USERS:
        username = ACCEPTABLE_USERS[number]
    else:
        message = 'Unauthorized request'
        resp.message(message)
        return resp

    step, check_in_id = get_step_id(username)

    with open('emotions/config.json') as f:
        emotions = json.load(f)

    core = ['love', 'joy', 'surprise', 'sadness', 'anger', 'fear']

    if step == 1:
        emotion = process.extractOne(text, core)[0]
        sql = 'UPDATE check_ins SET emotion1 = ? WHERE check_in_id = ?'
        notebook.model.update_db(sql, (emotion, check_in_id))
        message = "Please select the emotion that best describes how you felt:"
        for emotion in emotions[emotion]:
            message += ' ' + emotion
        resp.message(message)
    elif step == 2:
        sql = 'SELECT emotion1 FROM check_ins WHERE check_in_id = ?'
        core_emotion = notebook.model.query_db(sql, (check_in_id,))[0]['emotion1']
        prev_emotions = []
        for prev_emotion in emotions[core_emotion]:
            prev_emotions.append(prev_emotion)
        emotion = process.extractOne(text, prev_emotions)[0]
        sql = 'UPDATE check_ins SET emotion2 = ? WHERE check_in_id = ?'
        notebook.model.update_db(sql, (emotion, check_in_id))
        message = "Please select the emotion that best describes how you felt:"
        for emotion in emotions[core_emotion][emotion]:
            message += ' ' + emotion
        resp.message(message)
    elif step == 3:
        sql = 'SELECT emotion1, emotion2 FROM check_ins WHERE check_in_id = ?'
        sel_emotions = notebook.model.query_db(sql, (check_in_id,))[0]
        prev_emotions = emotions[sel_emotions['emotion1']][sel_emotions['emotion2']]
        emotion = process.extractOne(text, prev_emotions)[0]
        sql = 'UPDATE check_ins SET emotion3 = ? WHERE check_in_id = ?'
        notebook.model.update_db(sql, (emotion, check_in_id))
        message = "Any thoughts?"
        resp.message(message)
    elif step == 4:
        sql = 'UPDATE check_ins SET thoughts = ? WHERE check_in_id = ?'
        notebook.model.update_db(sql, (text, check_in_id))
        message = "Any tags?"
        resp.message(message)
    elif step == 5:
        sql = 'UPDATE check_ins SET tags = ? WHERE check_in_id = ?'
        notebook.model.update_db(sql, (text, check_in_id))
        message = "That is all. Thanks!"
        resp.message(message)
    else:
        message = "Oops! Something went wrong. Please check the logs now."
        resp.message(message)
    return resp
