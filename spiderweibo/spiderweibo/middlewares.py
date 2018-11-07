# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import logging, requests, json
from scrapy.exceptions import IgnoreRequest


class SpiderweiboSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeiboDownloaderMiddleware(object):
    def __init__(self, cookie_pool_url):
        self.cookie_pool_url = cookie_pool_url
        self.logger = logging.getLogger("__file__")

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(cookie_pool_url=crawler.settings.get("COOKIE_POOL_URL"))
        return s

    def __get_random_cookie(self):
        response = requests.get(self.cookie_pool_url)
        try:
            if response.status_code == 200:
                return json.loads(response.text)
        except ConnectionError:
            return None

    def process_request(self, request, spider):
        cookies = self.__get_random_cookie()
        self.logger.debug("Getting Cookies")
        if cookies:
            request.cookies = cookies
            self.logger.debug("Using Cookies")
        else:
            self.logger.debug("Not Getting Cookies")

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                redirct_url = request.headers["location"]
                if "passport" in redirct_url:
                    self.logger.warning("Need Update Cookies")
                elif "weibo.cn/security" in redirct_url:
                    self.logger.warning("Account is Baned")
                request.cookies = self.__get_random_cookie()
                return request
            except:
                raise IgnoreRequest

        elif response.status == 414:
            return request
        else:
            return response