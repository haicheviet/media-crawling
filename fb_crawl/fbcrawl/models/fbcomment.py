import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.mysql import TEXT

from fbcrawl.models.base import generate_uuid, DeclarativeBase


class FbComment(DeclarativeBase):
    """Sqlalchemy model"""

    __tablename__ = "fb_comment"
    comment_id = Column("comment_id", String(30), primary_key=True)
    source = Column("source", String(300))
    reply_to = Column("reply_to", String(300))
    text = Column("text", TEXT)
    last_update = Column("last_update", DateTime)
    reactions = Column("reactions", Integer)
    post_id = Column("post_id", String(300))
    source_url = Column("source_url", String(300))
    url = Column("url", String(300))
    create_date = Column(
        "create_date", DateTime, default=datetime.datetime.utcnow, nullable=True
    )
    sentiment = Column("sentiment", String(300))
