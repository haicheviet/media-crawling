import traceback

import celery
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from app.task.celery_app import celery_app  # noqa: F401
from app.task.scrapy_crawl_news.crawl_news.spiders.news import NewsSpider


@celery.task()
def crawl_social_scrip():
    process = CrawlerProcess(get_project_settings())
    try:
        process.crawl(NewsSpider)
        process.start()  # the script will block here until the crawling is finished
    except:  # noqa E722
        traceback.print_exc()
