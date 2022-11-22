from operator import pos
import traceback
import scrapy
import logging

from scrapy.loader import ItemLoader
from scrapy.http import FormRequest, request
from scrapy.exceptions import CloseSpider
from fbcrawl.items import FbcrawlItem, parse_date, parse_date2, parse_date3
from datetime import datetime, time
from tqdm import tqdm
from random import randint, random
import time



tsmin = 1
tsmax = 1

class FacebookSpider(scrapy.Spider):
    """
    Parse FB pages (needs credentials)
    """

    name = "fb_crawl_list_post"
    custom_settings = {
        "FEED_EXPORT_FIELDS": [
            "source",
            "shared_from",
            "date",
            "text",
            "reactions_text",
            "likes",
            "ahah",
            "love",
            "wow",
            "sigh",
            "grrr",
            "comments",
            "post_id",
            "url",
        ],
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "ITEM_PIPELINES": {
            "fbcrawl.pipelines.FbPostPipeline": 300,
        },
    }

    def __init__(self, *args, **kwargs):
        #turn off annoying logging, set LOG_LEVEL=DEBUG in settings.py to see more logs
        logger = logging.getLogger('scrapy.middleware')
        logger.setLevel(logging.WARNING)
        
        super().__init__(*args,**kwargs)
        
        #email & pass need to be passed as attributes!
        if 'email' not in kwargs or 'password' not in kwargs:
            raise AttributeError('You need to provide valid email and password:\n'
                                 'scrapy fb -a email="EMAIL" -a password="PASSWORD"')
        else:
            self.logger.info('Email and password provided, will be used to log in')

        #page name parsing (added support for full urls)
        
        if 'page' in kwargs:
            if self.page.find('/groups/') != -1:
                self.group = 1
            else:
                self.group = 0
            if self.page.find('https://www.facebook.com/') != -1:
                self.page = self.page[25:]
            elif self.page.find('https://mbasic.facebook.com/') != -1:
                self.page = self.page[28:]
            elif self.page.find('https://m.facebook.com/') != -1:
                self.page = self.page[23:]
        self.group = 1

        #parse date
        if 'date' not in kwargs:
            self.logger.info('Date attribute not provided, scraping date set to 2004-02-04 (fb launch date)')
            self.date = datetime(2004,2,4)
        else:
            self.date = datetime.strptime(kwargs['date'],'%Y-%m-%d')
            self.logger.info('Date attribute provided, fbcrawl will stop crawling at {}'.format(kwargs['date']))
        self.year = self.date.year

        #parse lang, if not provided (but is supported) it will be guessed in parse_home
        if 'lang' not in kwargs:
            self.logger.info('Language attribute not provided, fbcrawl will try to guess it from the fb interface')
            self.logger.info('To specify, add the lang parameter: scrapy fb -a lang="LANGUAGE"')
            self.logger.info('Currently choices for "LANGUAGE" are: "en", "es", "fr", "it", "pt"')
            self.lang = '_'                       
        elif self.lang == 'en'  or self.lang == 'es' or self.lang == 'fr' or self.lang == 'it' or self.lang == 'pt':
            self.logger.info('Language attribute recognized, using "{}" for the facebook interface'.format(self.lang))
        else:
            self.logger.info('Lang "{}" not currently supported'.format(self.lang))                             
            self.logger.info('Currently supported languages are: "en", "es", "fr", "it", "pt"')                             
            self.logger.info('Change your interface lang from facebook settings and try again')
            raise AttributeError('Language provided not currently supported')
        
        #max num of posts to crawl
        if 'max' not in kwargs:
            self.max = int(10e5)
        else:
            self.max = int(kwargs['max'])
    
        #current year, this variable is needed for proper parse_page recursion
        self.k = datetime.now().year
        #count number of posts, used to enforce DFS and insert posts orderly in the csv
        self.count = 0
        
        self.start_urls = ['https://mbasic.facebook.com']    

    def parse(self, response):
        '''
        Handle login with provided credentials
        '''
        print(self.email, self.password)
        return FormRequest.from_response(
                response,
                formxpath='//form[contains(@action, "login")]',
                formdata={'email': self.email,'pass': self.password},
                callback=self.parse_home
                )
  
    def parse_home(self, response):
        '''
        This method has multiple purposes:
        1) Handle failed logins due to facebook 'save-device' redirection
        2) Set language interface, if not already provided
        3) Navigate to given page 
        '''
        #handle 'save-device' redirection
        with open("temp.html", "w") as f:
            f.write(response.body.decode("utf-8"))
        # if response.xpath("//div/a[contains(@href,'save-device')]"):
        #     self.logger.info('Going through the "save-device" checkpoint')
        #     return FormRequest.from_response(
        #         response,
        #         formdata={'nux_source': 'regular_login'},
        #         callback=self.parse_home
        #         )
            
        #set language interface
        if self.lang == '_':
            if response.xpath("//input[@placeholder='Search Facebook']"):
                self.logger.info('Language recognized: lang="en"')
                self.lang = 'en'
            elif response.xpath("//input[@placeholder='Buscar en Facebook']"):
                self.logger.info('Language recognized: lang="es"')
                self.lang = 'es'
            elif response.xpath("//input[@placeholder='Rechercher sur Facebook']"):
                self.logger.info('Language recognized: lang="fr"')
                self.lang = 'fr'
            elif response.xpath("//input[@placeholder='Cerca su Facebook']"):
                self.logger.info('Language recognized: lang="it"')
                self.lang = 'it'
            elif response.xpath("//input[@placeholder='Pesquisa no Facebook']"):
                self.logger.info('Language recognized: lang="pt"')
                self.lang = 'pt'
            else:
                raise AttributeError('Language not recognized\n'
                                     'Change your interface lang from facebook ' 
                                     'and try again')
                                                                 
        #navigate to provided page
        self.logger.info('Scraping facebook page {}'.format(self.page))
        print(self.page)
        import numpy as np
        import os

        print(os.getcwd())
        post_list = np.load(f"{self.page}", allow_pickle=True)
        for i in tqdm(post_list):
            new = ItemLoader(item=FbcrawlItem())
            new.add_value("comments", None)
            new.add_value("date", i["date"])
            new.add_value("url", i["url"])
            new.add_value("post_id", i["post_id"])
            # new.add_value("source", self.page.split(".")[0])

            temp_post = i["url"]
            # time.sleep(randint(tsmin, tsmax))
            yield scrapy.Request(
                    temp_post, self.parse_post, priority=self.count, meta={"item": new}
                )

        # return scrapy.Request(url=href,callback=self.parse_page,meta={'index':1})

    def parse_page(self, response):
        # from scrapy.shell import inspect_response

        # inspect_response(response, self)
        for post in response.xpath("//article[contains(@data-ft,'top_level_post_id')]"):

            many_features = post.xpath("./@data-ft").get()
            date_list = []
            date_list.append(many_features)
            date = parse_date(date_list, {"lang": self.lang})
            current_date = (
                datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                if date is not None
                else date
            )

            if current_date is None:
                date_string = post.xpath(".//abbr/text()").get()
                date = parse_date3(date_string)
                current_date = (
                    datetime(date.year, date.month, date.day)
                    if date is not None
                    else date
                )
                date = str(date)

            # if 'date' argument is reached stop crawling
            if self.date > current_date:
                raise CloseSpider("Reached date: {}".format(self.date))

            new = ItemLoader(item=FbcrawlItem(), selector=post)
            if abs(self.count) + 1 > self.max:
                raise CloseSpider(
                    "Reached max num of post: {}. Crawling finished".format(
                        abs(self.count)
                    )
                )
            self.logger.info(
                "Parsing post n = {}, post_date = {}".format(abs(self.count) + 1, date)
            )
            # print(post)
            # print(post.xpath(".//a[contains(@data-sigil,'comments-token')]/text()").get())
            # post.xpath(".//a[contains(text(),'Comments')]/text()")
            new.add_xpath("comments", ".//a[contains(text(),'Comments')]/text()")
            new.add_value("date", date)
            new.add_xpath("post_id", "./@data-ft")
            new.add_xpath("url", ".//a[contains(@href,'footer')]/@href")
            # from scrapy.shell import inspect_response

            # inspect_response(response, self)

            # returns full post-link in a list
            post = post.xpath(".//a[contains(@href,'footer')]/@href").extract()
            temp_post = response.urljoin(post[0])
            self.count -= 1
            yield scrapy.Request(
                temp_post, self.parse_post, priority=self.count, meta={"item": new}
            )

        # load following page, try to click on "more"
        # after few pages have been scraped, the "more" link might disappears
        # if not present look for the highest year not parsed yet
        # click once on the year and go back to clicking "more"

        # new_page is different for groups

        if self.group == 1:
            new_page = response.xpath(
                "//div[contains(@id,'m_group_stories_container')]/div/a/@href"
            ).extract()
            # if not new_page:
            #     # See more posts in vn page
            #     print("sss")
            #     new_page = response.xpath(
            #         "//div[2]/a[contains(@href,'bacr=') and not(contains(text(),'ent')) and not(contains(text(),number()))]/@href").extract()
        else:
            new_page = response.xpath(
                "//div[2]/a[contains(@href,'timestart=') and not(contains(text(),'ent')) and not(contains(text(),number()))]/@href"
            ).extract()

            # this is why lang is needed
        return
        if not new_page:
            
            self.logger.info('[!] "more" link not found, will look for a "year" link')
            # self.k is the year link that we look for
            if response.meta["flag"] == self.k and self.k >= self.year:
                xpath = (
                    "//div/a[contains(@href,'time') and contains(text(),'"
                    + str(self.k)
                    + "')]/@href"
                )
                new_page = response.xpath(xpath).extract()
                if new_page:
                    new_page = response.urljoin(new_page[0])
                    self.k -= 1
                    self.logger.info(
                        'Found a link for year "{}", new_page = {}'.format(
                            self.k, new_page
                        )
                    )
                    yield scrapy.Request(
                        new_page, callback=self.parse_page, meta={"flag": self.k}
                    )
                else:
                    while (
                        not new_page
                    ):  # sometimes the years are skipped this handles small year gaps
                        self.logger.info(
                            "Link not found for year {}, trying with previous year {}".format(
                                self.k, self.k - 1
                            )
                        )
                        self.k -= 1
                        if self.k < self.year:
                            raise CloseSpider(
                                "Reached date: {}. Crawling finished".format(self.date)
                            )
                        xpath = (
                            "//div/a[contains(@href,'time') and contains(text(),'"
                            + str(self.k)
                            + "')]/@href"
                        )
                        new_page = response.xpath(xpath).extract()
                    self.logger.info(
                        'Found a link for year "{}", new_page = {}'.format(
                            self.k, new_page
                        )
                    )
                    new_page = response.urljoin(new_page[0])
                    self.k -= 1
                    yield scrapy.Request(
                        new_page, callback=self.parse_page, meta={"flag": self.k}
                    )
            else:
                self.logger.info("Crawling has finished with no errors!")
        else:
            new_page = response.urljoin(new_page[0])
            if "flag" in response.meta:
                self.logger.info(
                    'Page scraped, clicking on "more"! count: {} new_page = {}'.format(
                        self.count, new_page
                    )
                )
                yield scrapy.Request(
                    new_page,
                    callback=self.parse_page,
                    meta={"flag": response.meta["flag"]},
                )
            else:
                self.logger.info(
                    'First page scraped, clicking on "more"! new_page = {}'.format(
                        new_page
                    )
                )
                yield scrapy.Request(
                    new_page, callback=self.parse_page, meta={"flag": self.k}
                )

    def parse_post(self, response):
        time.sleep(randint(tsmin, tsmax))
        # print("ssss")
        new = ItemLoader(
            item=FbcrawlItem(), response=response, parent=response.meta["item"]
        )
        # print(response.meta["item"].value)
        new.context["lang"] = self.lang
        new.add_xpath(
            "source",
            "//td/div/h3/strong/a/text() | //span/strong/a/text() | //div/div/div/a[contains(@href,'post_id')]/strong/text()",
        )
        new.add_xpath(
            "shared_from",
            '//div[contains(@data-ft,"top_level_post_id") and contains(@data-ft,\'"isShare":1\')]/div/div[3]//strong/a/text()',
        )
        #   new.add_xpath('date','//div/div/abbr/text()')
        new.add_xpath(
            "text",
            "//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()",
        )

        # check reactions for old posts

        check_reactions = response.xpath(
            "//a[contains(@href,'reaction/profile')]/div/div/text()"
        ).get()
        if not check_reactions:
            check_reactions = response.xpath(
                "//a[contains(@aria-label,'reactions, including Like')]/text()"
            ).get()
            if not check_reactions:
                yield new.load_item()
            else:
                print("ddd")
                new.add_xpath(
                    "reactions_text",
                    "//a[contains(@aria-label,'reactions, including Like')]/text()",
                )
                post_link = response.xpath(
                    "//a[contains(@aria-label,'reactions, including Like')]/@href"
                ).get()
                # from scrapy.shell import inspect_response

                # inspect_response(response, self)
                post_link = response.urljoin(post_link[0].extract())
                yield scrapy.Request(
                    post_link, callback=self.wrapper_reaction, meta={"item": new}
                )
        else:
            new.add_xpath(
                "reactions_text",
                "//a[contains(@href,'reaction/profile')]/div/div/text()",
            )
            reactions = response.xpath(
                "//div[contains(@id,'sentence')]/a[contains(@href,'reaction/profile')]/@href"
            )
            reactions = response.urljoin(reactions[0].extract())

            # Reaction some page is fail from fb
            yield scrapy.Request(
                reactions,
                callback=self.parse_reactions,
                meta={"item": new},
                errback=self.errback,
            )

    def wrapper_reaction(self, response):
        new = ItemLoader(
            item=FbcrawlItem(), response=response, parent=response.meta["item"]
        )
        reactions = response.xpath(
            "//div[contains(@id,'sentence')]/a[contains(@href,'reaction/profile')]/@href"
        )
        reactions = response.urljoin(reactions[0].extract())

        yield scrapy.Request(
            reactions,
            callback=self.parse_reactions,
            meta={"item": new},
            cb_kwargs={"item": new},
        )

    def parse_reactions(self, response):
        new = ItemLoader(
            item=FbcrawlItem(), response=response, parent=response.meta["item"]
        )

        new.context["lang"] = self.lang
        new.add_xpath("likes", "//a[contains(@href,'reaction_type=1')]/span/text()")
        new.add_xpath("ahah", "//a[contains(@href,'reaction_type=4')]/span/text()")
        new.add_xpath("love", "//a[contains(@href,'reaction_type=2')]/span/text()")
        new.add_xpath("wow", "//a[contains(@href,'reaction_type=3')]/span/text()")
        new.add_xpath("sigh", "//a[contains(@href,'reaction_type=7')]/span/text()")
        new.add_xpath("grrr", "//a[contains(@href,'reaction_type=8')]/span/text()")
        yield new.load_item()

    def errback(self, failure):
        new = failure.value.response.meta["item"]

        self.logger.info(
            "Handled by the errback: %s (%s exception)",
            failure.request.url,
            str(failure.value),
        )
        yield new.load_item()