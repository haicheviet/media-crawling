import datetime
import os

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.mysql import TEXT

from fbcrawl.models.base import generate_uuid, DeclarativeBase


class FbPost(DeclarativeBase):
    """Sqlalchemy model"""

    __tablename__ = "fb_post"

    id = Column(String(255), name="id", primary_key=True, default=generate_uuid)
    source = Column("source", String(300))
    shared_from = Column("shared_from", String(300))

    reply_to = Column("reply_to", String(300))
    text = Column("text", TEXT)
    last_update = Column("last_update", DateTime)
    reactions_text = Column("reactions_text", String(300))
    reactions = Column("reactions", Integer)
    likes = Column("likes", Integer)
    ahah = Column("ahah", Integer)
    love = Column("love", Integer)
    wow = Column("wow", Integer)
    sigh = Column("sigh", Integer)
    grrr = Column("grrr", Integer)
    comments = Column("comments", Integer)
    post_id = Column("post_id", String(300))
    url = Column("url", String(300))
    create_date = Column(
        "create_date", DateTime, default=datetime.datetime.utcnow, nullable=True
    )
