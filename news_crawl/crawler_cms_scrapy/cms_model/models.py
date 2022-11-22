import datetime
import os

from sqlalchemy import Column, String, DateTime

import uuid
from sqlalchemy.engine import create_engine
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection.
    Returns sqlalchemy engine instance
    """
    return create_engine(os.getenv("DATABASE_URL"))


def create_news_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

def generate_uuid():
    return str(uuid.uuid4())

class NewsPaper(DeclarativeBase):
    """Sqlalchemy model"""
    __tablename__ = "news"

    id = Column(String(255), name="id", primary_key=True, default=generate_uuid)
    url = Column('url', String(300))
    keyword = Column('keyword', String(200))
    summary = Column('summary', String(200))
    source = Column('source', String(100))
    title = Column('title', String(200))
    location = Column('location', String(50))
    last_update = Column('last_update', DateTime, nullable=False)
    create_date = Column('create_date', DateTime, default=datetime.datetime.utcnow, nullable=True)


class NewsPage(DeclarativeBase):
    """Sqlalchemy model"""
    __tablename__ = "news_page"
    id = Column(String(255), name="id", primary_key=True, default=generate_uuid)
    url = Column('url', String(300), unique=True, nullable=False)
    title = Column('title', TEXT)
    description = Column("description", TEXT)
    img_url = Column('img_url', String(300))
    last_update = Column('last_update', DateTime, nullable=True)
    create_date = Column('create_date', DateTime, default=datetime.datetime.utcnow, nullable=True)
