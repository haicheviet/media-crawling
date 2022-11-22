# -*- coding: utf-8 -*-
# from scrapy.http import Request
# from scrapy.http.response.html import HtmlResponse
from urllib.parse import urlparse

from newspaper import Article
from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from underthesea import ner

from crawler_cms_scrapy.items import NewsItem

name_crawl = "vnexpress"


class VnexpressSpider(CrawlSpider):
    name = name_crawl

    rules = [
        Rule(LinkExtractor(allow=[r"\-\d*\.html"], deny=[r"https://\w+.vnexpress"]), callback='parse_item')
    ]

    def parse_item(self, response):
        item = NewsItem()
        article = Article("random_url")
        article.download(input_html=response.body)
        article.parse()
        article.nlp()
        location = None
        for ner_item in ner(article.title):
            if ner_item[3] == "B-LOC":
                location = ner_item[0]
                if len(location) <= 1:
                    location = None
        item["url"] = response.url
        item["keyword"] = ";".join(article.keywords)
        item["summary"] = ";".join(article.summary.split("\n"))
        item["title"] = article.title
        item["location"] = location
        item["source"] = urlparse(response.url).netloc
        item["last_update"] = article.publish_date

        self.log(f"Done crawling: {response.url}")
        yield item

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = cls(*args, **kwargs)
    #     spider._set_crawler(crawler)
    #     spider.crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
    #     return spider
    #
    # def spider_idle(self):
    #     self.log("Spider idle signal caught.")
    #     raise DontCloseSpider

#
# class VnexpressSpider(CrawlSpider):
#     name = name_crawl
#
#     # allowed_domains = ['vnexpress.net']
#     # start_urls = ['http://vnexpress.net/', ]
#     # rules = [
#     #     Rule(LinkExtractor(allow=[r"\-\d*\.html"], deny=[r"https://\w+.vnexpres"]), callback='parse_item')
#     # ]
#     # start_urls = ['http://vnexpress.net/', ]
#     def __init__(self, *args, **kwargs):
#         super(VnexpressSpider, self).__init__(*args, **kwargs)
#
#         self.le = LinkExtractor(allow=[r"\-\d*\.html"], deny=[r"https://\w+.vnexpres"])
#
#     def parse(self, response):
#         if not isinstance(response, HtmlResponse):
#             return
#
#         for link in self.le.extract_links(response):
#             print(link.url)
#             r = Request(url=link.url, callback=self.parse_item)
#             r.meta.update(link_text=link.text)
#             yield r
#
#     def parse_item(self, response):
#         item = NewsItem()
#         article = Article("random_url")
#         article.download(input_html=response.body)
#         article.parse()
#         article.nlp()
#         location = None
#         for ner_item in ner(article.title):
#             if ner_item[3] == "B-LOC":
#                 location = ner_item[0]
#         if len(location) <= 1:
#             location = None
#         item["url"] = response.url
#         item["keyword"] = ";".join(article.keywords)
#         item["summary"] = ";".join(article.summary.split("\n"))
#         item["title"] = article.title
#         item["location"] = location
#         item["source"] = name_crawl
#
#         self.log(f"Done crawling: {response.url}")
#         yield item
