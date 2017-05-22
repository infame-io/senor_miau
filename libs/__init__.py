__author__ = 'infame-io'
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from model import Jobs
from settings import LOG_FILENAME, session

scheduler = BackgroundScheduler()
scheduler.start()

logging.getLogger(__name__)

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s') #,
                    # datefmt="%Y-%m-%d %H:%M:%S") remove milliseconds from timestamp


def get_db_session():
    return session()


def jobs_cleaner():
    try:
        session = get_db_session()

        jobs = session.query(Jobs).filter_by(is_booked=True, has_url=True)

        if jobs.count() > 0:
            jobs_cleaned = jobs.delete(synchronize_session=False)
            session.commit()
            logging.info("{} jobs cleaned from the database".format(jobs_cleaned))

        session.close()

    except Exception as e:
        logging.error("Exception raised {}".format(e))
