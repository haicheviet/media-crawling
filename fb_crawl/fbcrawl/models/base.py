import uuid
import os

from sqlalchemy.engine import create_engine
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