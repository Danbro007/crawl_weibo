# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, time
from .items import SpiderweiboItem
import pymongo


class SpiderweiboPipeline(object):
    def format_time(self, date_time):
        if re.match("\d+月\d+日", date_time):
            date_time = (time.strftime("%Y{y}", time.localtime()) + date_time).format(y="年")
        elif re.match("\d+分钟前", date_time):
            minute = re.search("(.*?)分钟前", date_time).group(1)
            date_time = (time.strftime("%Y{y}%m{m}%d{d} %H{H}:%M{M}", time.localtime(time.time() - float(minute) * 60))).format(y="年", m="月", d="日", H="时", M="分")
        elif re.match("今天.*", date_time):
            date_time = re.search("今天(.*)", date_time).group(1).strip()
            date_time = (time.strftime("%Y{y}%m{m}%d{d}", time.localtime()) + " " + date_time).format(y="年", m="月", d="日")
        else:
            hour, minute = date_time.split(":", 2)[0], date_time.split(":", 2)[1]
            date_time = hour + ":" + minute
        return date_time

    def process_item(self, item, spider):
        if isinstance(item, SpiderweiboItem):
            if item["posted_at"]:
                date_time = self.format_time(item["posted_at"])
                item["posted_at"] = date_time
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item.table_name].update({"id":item["id"]}, {"$set": dict(item)},True)
        return item