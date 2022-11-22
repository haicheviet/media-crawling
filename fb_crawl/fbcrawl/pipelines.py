# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# from scrapy.exceptions import DropItem
# from datetime import datetime

from sqlalchemy.orm import sessionmaker
import traceback
from fbcrawl.models.fbcomment import FbComment
from fbcrawl.models.fbpost import FbPost
from fbcrawl.models.base import db_connect, create_news_table


class FbcrawlPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates news table.
        """
        engine = db_connect()
        create_news_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save items in the database."""
        session = self.Session()
        fb_comment_item = dict(item)
        if not fb_comment_item.get("text"):
            spider.logger.info("Text is empty")
            return item
        
        if type(fb_comment_item.get("source_url")) == list:
            fb_comment_item["source_url"] = fb_comment_item["source_url"][0]
        if type(fb_comment_item["comment_id"]) == list:
            for comment_item in fb_comment_item["comment_id"]:
                if comment_item.isdigit():
                    fb_comment_item["comment_id"] = comment_item
                    break
                
            if type(fb_comment_item["comment_id"]) == list:
                fb_comment_item["comment_id"] = fb_comment_item["comment_id"][0]
        if not fb_comment_item["comment_id"].isdigit():
            fb_comment_item["comment_id"] = fb_comment_item["comment_id"].split("_")[-1]
        fb_comment = FbComment(**fb_comment_item)
        fb_indb = session.query(FbComment).filter_by(comment_id=fb_comment.comment_id).first()      
        if fb_indb is None:
            try:
                session.add(fb_comment)
                session.commit()
            except:
                spider.logger.info(f"{traceback.format_exc()}")
                session.rollback()
                raise
            finally:
                session.close()
        else:
            spider.logger.info("<-------------------------------------------->")
            spider.logger.info(f"{fb_indb.comment_id}: {fb_indb.text}")
            spider.logger.info("<---------ALREADY IN ------------------------->")
        return item


def parse_number(str_number: str):
    str_number = str_number.lower()
    if not str_number:
        return 0
    if str_number.isdigit():
        return int(str_number)
    if "k" in str_number:
        str_number = str_number.replace("k", "000")
    if "," in str_number:
        str_number = str_number.replace(",", "")
    if "." in str_number:
        str_number = str_number.replace(".", "")

    return int(str_number)


def parse_reaction_number(reaction_text):
    if type(reaction_text) == int:
        return reaction_text
    reaction_text_list = reaction_text.split()
    for i in reaction_text_list:
        if i.isdigit():
            return int(i)
        elif "K" == i[-1]:
            return parse_number(i)
        else:
            pass
    return 0


class FbPostPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates news table.
        """
        engine = db_connect()
        create_news_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save items in the database."""
        session = self.Session()
        fb_item = dict(item)
        # fb_item["date"]
        fb_item["likes"] = (
            parse_number(fb_item.get("likes")) if fb_item.get("likes") else 0
        )
        fb_item["love"] = (
            parse_number(fb_item.get("love")) if fb_item.get("love") else 0
        )
        fb_item["wow"] = (
            parse_number(fb_item.get("wow")) if fb_item.get("wow") else 0
        )
        fb_item["ahah"] = (
            parse_number(fb_item.get("ahah")) if fb_item.get("ahah") else 0
        )
        fb_item["sigh"] = (
            parse_number(fb_item.get("sigh")) if fb_item.get("sigh") else 0
        )
        fb_item["grrr"] = (
            parse_number(fb_item.get("grrr")) if fb_item.get("grrr") else 0
        )
        fb_item["comments"] = (
            parse_number(fb_item.get("comments")) if fb_item.get("comments") else 0
        )
        
        fb_item["post_id"] = fb_item["post_id"].strip()
        fb_item["reactions"] = parse_reaction_number(fb_item.get("reactions_text", 0))
        fb_item["last_update"] = fb_item["date"][0] if type(fb_item["date"]) == list else fb_item["date"]
        fb_item["source"] = fb_item["source"][0] if type(fb_item["source"]) == list else fb_item["source"]
        del fb_item["date"]
        fb_post = FbPost(**fb_item)
        fb_post_indb = session.query(FbPost).filter_by(post_id=fb_post.post_id).first()
        if fb_post_indb is None:
            try:
                session.add(fb_post)
                session.commit()
            except:
                spider.logger.info(f"{traceback.format_exc()}")
                session.rollback()
                raise
            finally:
                session.close()
        else:
            spider.logger.info("<-------------------------------------------->")
            spider.logger.info(fb_post_indb.text)
            spider.logger.info("<---------ALREADY IN ------------------------->")
        return item