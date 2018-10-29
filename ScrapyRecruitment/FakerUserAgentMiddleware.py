
"""
    A simple fake useragent  middleware
"""
from fake_useragent import UserAgent
import logging

class FakerUserAgentMiddleware:
    """Custom FakerUserAgentMiddleware."""

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self,setting):
        self.ua = UserAgent()


    def process_request(self,request,spider):
        if 'fake_useragent' not in request.meta or request.meta['fake_useragent'] == False:
            user_agent = self.ua.random
            request.headers.setdefault(b'User-Agent',user_agent)
