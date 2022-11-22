import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.mysql import TEXT

from fbcrawl.models.base import generate_uuid, DeclarativeBase

class FbPage(DeclarativeBase):
    """Sqlalchemy model"""
    __tablename__ = "fb_page"
    id = Column(String(255), name="id", primary_key=True, default=generate_uuid)
    url = Column('url', String(300), unique=True, nullable=False)
    title = Column('title', TEXT)
    description = Column("description", TEXT)
    img_url = Column('img_url', String(300))
    follow = Column("follow", Integer)
    last_update = Column('last_update', DateTime, nullable=True)
    create_date = Column('create_date', DateTime, default=datetime.datetime.utcnow, nullable=True)
