import scrapy
import json
import sys
import os
import logging
import jsonlines
import re
from scrapy import Request
from scrapy import signals
from urllib.parse import urlparse
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str




class BossJobDescSpider(RedisSpider):
    name = "BossJobDesc"
    baseurl = "https://www.zhipin.com"
    job_count = 0
 
    custom_settings= {
        'REDIS_START_URLS_KEY':'BossJobUrl:job_pre_items',
        'REDIS_ITEMS_KEY':'BossJobInfo:items'
    }


    def make_request_from_data(self, data):
        """Returns a Request instance from data coming from Redis. By default, ``data`` is an encoded URL. You can override this method to provide your own message decoding.
        Parameters
        ----------
        data : bytes
        Message from redis.

        Note: override RedisSpider to make it support to extract url from dictionary
        """

        data = bytes_to_str(data, self.redis_encoding)
        data = json.loads(data)
        url = data['job_url']
        request = Request(url)
        request.meta['job_info'] = data
        return request

    def parse(self,response):
        """Parse the job details"""
        job_info = response.meta['job_info']
        job_desc = response.xpath('//div[contains(@class,"job-sec")]/div[contains(@class,"text")]/text()').extract()
        job_comloc = response.xpath('//div[contains(@class,"location-address")]/text()').extract()
        job_info['job_desc'] = ''.join(str(desc) for desc in job_desc)
        job_info['job_location_detail'] = job_comloc
        self.job_count += 1;
        self.logger.info("Found "+str(self.job_count)+" jobs ...")
        yield job_info
