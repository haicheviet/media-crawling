# from twisted.enterprise import adbapi
import logging

from sqlalchemy.orm import sessionmaker

from app.models.news import News

logger = logging.getLogger(__name__)


class FundPipeLine(object):
    def process_item(self, item, spider):
        """Save items in the database."""
        session = self.Session()
        news = News(**item)
        news_indb = session.query(News).filter_by(url=news.url).first()
        if news_indb is None:
            try:
                session.add(news)
                session.commit()
            except:  # noqa
                session.rollback()
                raise
            finally:
                session.close()
        else:
            spider.logger.info("<-------------------------------------------->")
            spider.logger.info(news_indb.title)
            spider.logger.info("<---------ALREADY IN ------------------------->")
        return item


# class FundPipeline(object):
#     # The table you items.FundItem class map to, my table is named fund
#     insert_sql = """insert into fund (%s) values ( %s )"""
#
#     def __init__(self):
#         dbargs = settings.get('DB_CONNECT')
#         db_server = settings.get('DB_SERVER')
#         dbpool = adbapi.ConnectionPool(db_server, **dbargs)
#         self.dbpool = dbpool
#
#     def __del__(self):
#         self.dbpool.close()
#
#     def process_item(self, item, spider):
#         self.insert_data(item, self.insert_sql)
#         return item
#
#     def insert_data(self, item, insert):
#         keys = item.fields.keys()
#         fields = u','.join(keys)
#         qm = u','.join([u'%s'] * len(keys))
#         sql = insert % (fields, qm)
#         data = [item[k] for k in keys]
#         return self.dbpool.runOperation(sql, data)
