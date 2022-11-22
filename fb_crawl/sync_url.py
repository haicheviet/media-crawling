from datetime import datetime
from fbcrawl.models.base import db_connect, create_news_table
from fbcrawl.models.fb_page import FbPage
from sqlalchemy.orm import sessionmaker


engine = db_connect()
create_news_table(engine)
Session = sessionmaker(bind=engine)
session = Session()
with open("seed_url.txt", "r") as f:
    list_data = f.read().splitlines()

for item in list_data:
    item = {
        "url" : item,
        "last_update": datetime.now()
    }
    fb_page = FbPage(**item)
    fb_post_indb = session.query(FbPage).filter_by(url=fb_page.url).first()
    if fb_post_indb is None:
        session.add(fb_page)
        session.commit()