import scrapy.crawler as crawler
import os
from fbcrawl.spiders.fbcrawl_mfacebook_by_list_post import FacebookSpider
from twisted.internet import reactor
from multiprocessing import Process, Queue
from tqdm import tqdm
import logging
import sys
import traceback
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

with open("seed_url.txt", "r") as f:
    list_data = f.read().splitlines()


def run_spider(crawler_or_spidercls, *args, **kwargs):
    def f(q):
        try:
            runner = crawler.CrawlerProcess(settings)
            runner.crawl(crawler_or_spidercls, *args, **kwargs)
            runner.start()
            q.put(None)
        except Exception as e:
            traceback.print_exec()
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
import subprocess


# def run_spider(*args, **kwargs):
#     cmd  = "scrapy crawl fb"
#     for k, v in kwargs.items():
#         cmd += f" -a {k}={v}"
#     print(cmd)
#     result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
#     result.stdout
    
# for item in tqdm(list_data):
item = "l%E1%BB%85%20h%E1%BB%99i%20khinh%20kh%C3%AD%20c%E1%BA%A7u.npy"
run_spider(
    FacebookSpider,
    email=os.getenv("FACEBOOK_EMAIL"),
    password=os.getenv("FACEBOOK_PASSWORD"),
    page=item,
    date="2019-01-01",
    lang="en"
)