# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class SpiderweiboItem(scrapy.Item):
    table_name = "weibo"
    user = Field()
    id = Field()
    url = Field()
    content = Field()
    comment_count = Field()
    like_count = Field()
    forward = Field()
    posted_at = Field()
