__author__ = 'infame-io'
import time
import re
import logging

from splinter import Browser
from dateutil import parser

from model import Jobs
from settings import slack_client, PH_URL, PH_USERNAME, PH_PASSWORD
from libs import get_db_session, scheduler


def scratch_website():
    """
        Scratch website to find URLs for classes
    """
    result = list()
    session = get_db_session()
    # with Browser('phantomjs', wait_time=5,
    #              user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.6 (KHTML, like Gecko)') as browser:
    try:
        jobs = session.query(Jobs).filter_by(is_booked=False, has_url=False)
        if jobs.count() > 0:

            browser = Browser('phantomjs', wait_time=5, user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.6 (KHTML, like Gecko)')
            logging.info("Loading website {}".format(PH_URL))
            browser.visit(PH_URL)
            newstead = browser.find_by_id('tab-id-6-container')
            time.sleep(180)

            logging.info("Filtering Monday classes")
            newstead.find_by_id('day_Mon').click()
            time.sleep(5)

            logging.info("Filtering Tuesday classes")
            newstead.find_by_id('day_Tue').click()
            time.sleep(5)

            logging.info("Filtering Wednesday classes")
            newstead.find_by_id('day_Wed').click()
            time.sleep(5)

            logging.info("Filtering Thursday classes")
            newstead.find_by_id('day_Thu').click()
            time.sleep(5)

            logging.info("Filtering Friday classes")
            newstead.find_by_id('day_Fri').click()
            time.sleep(5)

            logging.info("Filtering Saturday classes")
            newstead.find_by_id('day_Sat').click()
            time.sleep(5)

            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', newstead.html)
            class_urls = [url for url in urls if url.endswith("=Class")]

            for job in jobs:
                day_week = parser.parse(job.date).strftime("%a")
                job_date = job.date.split(" ")
                url_date = r'{}\.\+{}\+{}%2C\+{}\+\+{}\+{}'.format(day_week, job_date[0], job_date[1], job_date[2],
                                                                   job.time[:-2].replace(":", "%3A"), job.time[-2:])
                url_class = r'{}'.format(job.name.replace(" ", "\+"))

                for class_url in class_urls:
                    if re.match(r'https://(.)+' + url_date + '(.)+' + url_class + '(.)+', class_url):
                        job.url = class_url
                        job.has_url = True
                        session.commit()
                        result.append(job)
                        logging.info("URL added for class {} {} {}".format(job.name, job.date, job.time))

            browser.quit()

        session.close()

        scheduler.add_job(book_classes)

        return result
    except Exception as e:
        logging.error("Exception raised {}".format(e))
        session.close()
        pass


def book_classes():
    """
        Book classes when system frees URL
    """
    result = list()
    session = get_db_session()

    try:
        jobs = session.query(Jobs).filter_by(is_booked=False, has_url=True)
        confirmation_msg = ""

        if jobs.count() > 0:
            classes = "classes" if jobs.count() > 1 else "class"
            jobs_msg = "Booking {} {}".format(jobs.count(), classes)
            logging.info(jobs_msg)
            slack_client.api_call("chat.postMessage", channel="#general", text=jobs_msg, as_user=True)

            for job in jobs:

                browser = Browser('phantomjs', wait_time=5, user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.6 (KHTML, like Gecko)')
                logging.info("Processing {} on {} at {}".format(job.name, job.date, job.time))
                browser.visit(job.url)
                time.sleep(180)

                browser.click_link_by_text('Next')
                time.sleep(30)

                browser.find_by_id('mb_client_session_username').fill(PH_USERNAME)
                time.sleep(5)

                browser.find_by_id('mb_client_session_password').fill(PH_PASSWORD)
                time.sleep(5)

                browser.find_by_name('button').first.click()
                time.sleep(30)

                browser.click_link_by_text('Book')
                time.sleep(5)

                day_week = parser.parse(job.date).strftime("%A")

                job_msg = "Class {} on {} {} at {} has been booked".format(job.name, day_week, job.date, job.time)
                confirmation_msg += job_msg + "\n"

                job.is_booked = True
                session.commit()

                result.append(job)
                logging.info(job_msg)

                browser.quit()

            if confirmation_msg:
                slack_client.api_call("chat.postMessage", channel="#general", text=confirmation_msg, as_user=True)
        session.close()
        return result
    except Exception as e:
        logging.error("Exception raised {}".format(e))
        session.close()
        pass
