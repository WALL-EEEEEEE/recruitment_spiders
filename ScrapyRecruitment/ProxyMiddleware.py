"""
This is a simple proxy for scrapy
The  proxy host format like: `http://host:port` or `http://username:password@host:port` 
"""

import random
from ScrapyRecruitment.ProxyRequest import ProxyRequest
import logging

class ProxyMiddleware(object):
    """Custom ProxyMiddleware."""
    _proxy = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self,settings):
        self._proxy = ProxyRequest()

    def process_request(self,request,spider):
        if 'enable_proxy' not in request.meta or request.meta['enable_proxy'] == True:
            request.meta['proxy'] = self._proxy.get()
