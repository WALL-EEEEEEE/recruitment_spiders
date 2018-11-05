from scrapy.downloadermiddlewares import retry 
from fake_useragent import UserAgent
from ScrapyRecruitment.ProxyRequest import ProxyRequest
from scrapy.utils.python import global_object_name
import logging

"""
A simple overwritten retrymiddleware

Add  a new rule for switching proxy and useragent while retrying
"""
logger = logging.getLogger(__name__)

class HeaderDebugMiddleware():
    def parse_request(self,request,spider):
        logger.info('Header Debug:')
        logger.info(request.headers)


