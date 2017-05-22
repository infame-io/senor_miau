__author__ = 'infame-io'
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Jobs(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    url = Column(String)
    is_booked = Column(Boolean, default=False)
    has_url = Column(Boolean, default=False)


engine = create_engine('sqlite:///db/jobs.db', pool_recycle=3600)

Base.metadata.create_all(engine)
