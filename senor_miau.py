__author__ = 'infame-io'
import time

from settings import slack_client

from libs import logging, scheduler, jobs_cleaner
from libs.purehealth import scratch_website
from libs.slack_bot import parse_slack_output, handle_command


if __name__ == "__main__":
    logging.info("Starting Senor Miau")

    scheduler.add_job(scratch_website, 'cron', id="scratch_website", day="*", hour="6-9", minute="*/20")
    scheduler.add_job(jobs_cleaner, 'cron', id="jobs_cleaner", day="*", hour="*/2")

    READ_WEBSOCKET_DELAY = 3 # 3 second delay between reading from firehose
    if slack_client.rtm_connect():
        logging.info("Senor Miau bot is connected and running")

        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        logging.error("Connection failed to Senor Miau")
