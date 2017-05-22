__author__ = 'infame-io'
import re

from model import Jobs
from libs import logging, get_db_session
from settings import slack_client, AT_BOT, BOOK_COMMAND, CANCEL_COMMAND, PENDING_COMMAND, JOB_REGEX


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "What kind of sorcery is this? Try using the following commands:\n*{}* " \
               "(e.g. book May 19 2017,5:30pm,Open GRC)\n*{}* (e.g. cancel 3,5,6,8)\n" \
               "*{}* (e.g pending)".format(BOOK_COMMAND, CANCEL_COMMAND, PENDING_COMMAND)

    logging.info("Handling command {} on channel {}".format(command, channel))
    if command.startswith(BOOK_COMMAND):

        job = command[5:]
        if re.match(JOB_REGEX, job):
            session = get_db_session()
            data = job.split(",")
            job = Jobs(date=data[0], time=data[1], name=data[2])
            session.add(job)
            session.commit()
            session.close()
            logging.info("New job {} {} {} added into the database".format(data[2], data[0], data[1]))
            response = "Class {} on {} at {} has been scheduled and it will be booked as soon as it becomes available".format(data[2], data[0], data[1])
        else:
            response = "I dunno that kind of format. Try *" + BOOK_COMMAND + "* command (e.g. book May 19 2017,5:30pm,Open GRC)"

    if command.startswith(CANCEL_COMMAND):

        if re.match(r'^\d+(?:,\d+)?', command[7:]):
            _jobs = re.sub(r'\s+', '', command[7:])
            confirmation_msg = ""
            ids = _jobs.split(",")
            session = get_db_session()

            jobs = session.query(Jobs).filter_by(is_booked=False)
            if jobs.count() > 0:

                for job in jobs:
                    if str(job.id) in ids:
                        session.delete(job)
                        session.commit()
                        ids.remove(str(job.id))
                        job_msg = "Job for class {} on {} at {} has been removed".format(job.name, job.date, job.time)
                        logging.info(job_msg)
                        confirmation_msg += job_msg + "\n"
            session.close()
            if confirmation_msg:
                response = confirmation_msg

        else:
            response = "Nope ... no idea what you meant. Try *" + CANCEL_COMMAND + "* command (e.g. cancel 3,5,6,8)"

    if command.startswith(PENDING_COMMAND):
        session = get_db_session()
        jobs = session.query(Jobs).filter_by(is_booked=False)

        if jobs.count() > 0:
            confirmation_msg = ""
            for job in jobs:
                confirmation_msg += "{}.- {} on {} at {}\n".format(job.id, job.name, job.date, job.time)
            response = confirmation_msg

        else:
            response = "No jobs have been scheduled yet"
        session.close()
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), output['channel']

    return None, None
