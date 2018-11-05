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

class RetryMiddleware(retry.RetryMiddleware):
    ua = None
    proxy = None
    switched_ua = None
    switched_proxy = None


    def __init__(self,settings):
        super().__init__(settings)
        self.ua = UserAgent()
        self.proxy = ProxyRequest()

    def switch_ua_proxy(self,request):
        self.switched_proxy = self.proxy.get(True)
        self.switched_ua = self.ua.random
        request.meta['proxy'] = self.switched_proxy
        request.meta['enable_proxy'] = False
        request.headers.setdefault(b'User-Agent',self.switched_ua)


    def _retry(self,request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            self.switch_ua_proxy(retryreq)
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s ", {'request': request, 'retries': retries, 'reason': reason},extra={'spider': spider})
            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})



