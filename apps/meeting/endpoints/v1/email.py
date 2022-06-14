'''
Path functions for /apps/meeting
'''
import datetime
import os
import random

from fastapi import status, APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from services.mongo_service import get_mongo

router = APIRouter()


# pylint: disable=too-few-public-methods
class Envs:
    """
    Environment for fastapi mail
    """
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')
    MAIL_TLS = True
    MAIL_SSL = False
    USE_CREDENTIALS = True
    VALIDATE_CERTS = True


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)


def get_matching_failure_text():
    """
    Returns failing text of email
    """
    return """
Hello,
this is GaussTalk. 

We are sorry to inform you that the 1:1 matching you have requested have failed due to insufficient participants.
If you would like to do random 1:1s tomorrow please register by our website.
We will match you as soon as possible.

Sorry for the inconvenience.

GaussTalk 
    """


def get_matching_success_text(recipient, matched_recipient_list):
    """
    Returns success text of email
    """
    matched_opponents = None
    for group in matched_recipient_list:
        if recipient in group:
            others = [x for x in group if x != recipient]
            matched_opponents = others

    opponent_string = ""
    if len(matched_opponents) > 1:
        opponent_string = matched_opponents[0] + " and " + matched_opponents[1]
    else:
        opponent_string = matched_opponents[0]
    return """
Hello,
this is GaussTalk. 
Below includes the email of your random 1:1.
Please contact your match to set up a time for your 1:1!

You (""" + recipient + """) have been matched with """ + opponent_string + """.

Enjoy your random 1:1!
GaussTalk
"""


@router.post("/")
async def simple_send(
        background_tasks: BackgroundTasks,
        database=Depends(get_mongo)
):
    """Get yesterday's email and send it"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # today = datetime.date.today()
    try:
        emails = (database.meetings.find({'date': yesterday.strftime('%Y-%m-%d')},
                                         {'_id': 0, 'date': 0}))
        recipients = []
        for email in emails:
            recipients.append(email['mail'])
    except (TypeError, KeyError):
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": "email sending failed"})

    def match_recipients(people):
        random.shuffle(people)
        list_of_groups = [people[i:i + 2] for i in range(0, len(people), 2)]
        if len(list_of_groups[-1]) == 1:
            solo = list_of_groups.pop()
            list_of_groups[-1].append(*solo)
        return list_of_groups

    fastmail = FastMail(conf)

    if len(recipients) == 0:
        return JSONResponse(status_code=200, content={"message": "no emails to send"})

    if len(recipients) == 1:
        text = get_matching_failure_text()
        message = MessageSchema(
            subject="1:1 Matching Complete",
            recipients=recipients,  # List of recipients, as many as you can pass
            body=text,
            subtype="plain"
        )
        background_tasks.add_task(fastmail.send_message, message)
    else:
        matched_recipients = match_recipients(recipients)
        for recipient in recipients:
            text = get_matching_success_text(recipient, matched_recipients)
            message = MessageSchema(
                subject="1:1 Matching Complete",
                recipients=[recipient],  # List of recipients, as many as you can pass
                body=text,
                subtype="plain"
            )
            background_tasks.add_task(fastmail.send_message, message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
