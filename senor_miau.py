__author__ = 'infame-io'
import time
from datetime import datetime, timedelta
from settings import slack_client, session

from libs import logging, scheduler, jobs_cleaner, phantomjs_cleaner
from libs.purehealth import scratch_website
from libs.slack_bot import parse_slack_output, handle_command


if __name__ == "__main__":
    logging.info("Starting Senor Miau")
    start_time = datetime.now()
    scheduler.add_job(scratch_website, 'cron', id="scratch_website", day="*", hour="7-8", minute="*/30")
    scheduler.add_job(jobs_cleaner, 'cron', id="jobs_cleaner", day="*", hour="*/6")

    if slack_client.rtm_connect():
        logging.info("Senor Miau bot is connected and running")

        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(3)

            if start_time + timedelta(hours=8) < datetime.now():
                logging.info("Freeing memory")
                scheduler.shutdown()
                session.remove()
                phantomjs_cleaner()
                break
    else:
        logging.error("Connection failed to Senor Miau")
