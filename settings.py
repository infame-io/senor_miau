__author__ = 'infame-io'
import os
from sqlalchemy.orm import sessionmaker, scoped_session
from model import engine
from slackclient import SlackClient


DBSession = sessionmaker(bind=engine, autoflush=True, autocommit=False)
session = scoped_session(DBSession)

PH_URL = os.environ["PH_URL"]
PH_USERNAME = os.environ["PH_USERNAME"]
PH_PASSWORD = os.environ["PH_PASSWORD"]

BOT_NAME = os.environ["BOT_NAME"]
BOT_ID = os.environ["BOT_ID"]

SLACK_TOKEN = os.environ["SLACK_TOKEN"]

AT_BOT = "<@" + BOT_ID + ">"
BOOK_COMMAND = "book"
CANCEL_COMMAND = "cancel"
PENDING_COMMAND = "pending"

slack_client = SlackClient(SLACK_TOKEN)

LOG_FILENAME = 'senor_miau.log'

JOB_REGEX = r'^(?:January|February|March|April|May|June|July|August|September|October|November|December)\s([1-9]|[12]\d|3[01])\s2017\,(1[0-2]|0?[1-9]):([0-5][0-9])(am|pm)\,[^\s\n]+'
