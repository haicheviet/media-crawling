import os

from sqlalchemy.orm import sessionmaker
from fbcrawl.models.fbpost import FbPost
from fbcrawl.models.fbcomment import FbComment

from fbcrawl.models.base import db_connect
from scrapy.crawler import CrawlerProcess
from fbcrawl.spiders.comments import CommentsSpider
from multiprocessing import Process, Queue
from tqdm import tqdm

from scrapy.utils.project import get_project_settings
settings = get_project_settings()


def run_spider(crawler_or_spidercls, *args, **kwargs):
    def f(q):
        try:
            runner = CrawlerProcess(settings)
            runner.crawl(crawler_or_spidercls, *args, **kwargs)
            runner.start()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

engine = db_connect()
Session = sessionmaker(bind=engine)
session = Session()
fb_posts = session.query(FbPost).filter(FbPost.source!='Thấm').order_by(FbPost.create_date.desc()).limit(40).all()
for fb_post in tqdm(fb_posts):
    fb_comment_temp = (
        session.query(FbComment).filter_by(post_id=fb_post.post_id).first()
    )
    post_url = fb_post.url if "https://" in fb_post.url else f"https://m.facebook.com{fb_post.url}"
    # print(fb_post.url, fb_post.source)
    if fb_comment_temp is None:
        run_spider(
            CommentsSpider,
            email=os.getenv("FACEBOOK_EMAIL"),
            password=os.getenv("FACEBOOK_PASSWORD"),
            post_id=fb_post.post_id,
            post=post_url,
            max="50"
        )