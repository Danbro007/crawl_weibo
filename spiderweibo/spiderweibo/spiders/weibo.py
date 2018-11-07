# -*- coding: utf-8 -*-
from scrapy import FormRequest, Spider, Request
import re
from ..items import SpiderweiboItem


class WeiboSpider(Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    strart_url = "https://weibo.cn/search/mblog"
    max_page = 1
    keyword = "刘作虎"

    def start_requests(self):
        for page in range(self.max_page + 1):
            url = "{url}?keyword={keyword}".format(url=self.strart_url, keyword=self.keyword)
            data = {
                "mp": str(self.max_page),
                "page": str(page)
            }
            yield FormRequest(url=url, callback=self.index_parse, formdata=data)

    def index_parse(self, response):
        weibos = response.xpath('//div[@class="c" and contains(@id,"M_")]')
        for weibo in weibos:
            is_forword = bool(weibo.xpath('.//span[@class="cmt"]').extract_first())
            if is_forword:
                detail_url = weibo.xpath('.//a[contains(.,"原文评论")]//@href').extract_first()
            else:
                detail_url = weibo.xpath('.//a[contains(.,"评论")]//@href').extract_first()
            yield Request(url=detail_url, callback=self.detail_parse)

    def detail_parse(self, response):
        url = response.url
        content = "".join(response.xpath('//span[@class="ctt"]//text()').extract())
        user = response.xpath('.//div[@id="M_"]//div[1]//a//text()').extract_first()
        id = re.search("comment\/(.*?)\?", response.url).group(1)
        comment_count = response.xpath('//div[contains(.,"评论")]//text()').re_first("评论\[(.*?)\]", default=0)
        like_count = response.xpath('//a[contains(.,"赞")]//text()').re_first("赞\[(.*?)\]", default=0)
        forward_count = response.xpath('//a[contains(.,"转发")]//text()').re_first("转发\[(.*?)\]", default=0)
        posted_at = response.xpath('//span[@class="ct"]//text()').extract_first().strip()
        weibo_item = SpiderweiboItem()
        for field in weibo_item.fields:
            try:
                weibo_item[field] = eval(field)
            except NameError:
                self.logger.debug("This Field Is Not Defined")
        yield weibo_item




