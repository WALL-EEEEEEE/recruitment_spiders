
import scrapy
from scrapy import Spider
from scrapy.http import Response
from urllib.parse import urlparse
import re
import os
import json
import jsonlines

class BossJobPagesSpider (Spider):
    name = 'BossJobUrlSpider'
    allow_domains = ['www.zhipin.com']
    baseurl = 'http://www.zhipin.com'
    job_count = 0;
    page_count = 0;
    pages = []
    def start_requests(self):
        #load the categories list
        crequests = []
        with jsonlines.open('./data/BossJobCategory.jl') as reader:
            for cate in reader:
               clink = self.baseurl+cate['clink'][0]
               crequest = scrapy.FormRequest(clink,self.page_iterate)
               crequests.append(crequest)
        return crequests

    def page_iterate(self,response):
        # page_info
        print("Found "+ str(self.page_count)+" pages")
        last_page = response.xpath('//div[contains(@class,"page")]/a[ @ka="page-next" and contains(@class,"disabled")]');
        self.page_count += 1;
        current_url  = urlparse(response.url)
        yield {'page_url':current_url.geturl()}
        page_matcher = re.match('.*page=(\d+).*',current_url.query)
        current_page = 1 if not current_url.query or (page_matcher == None) else int(page_matcher.group(1))

        if not last_page and current_page < 20:
          if current_page == 1: 
               if not current_url.query:
                   next_page_clink = response.url+'?page=2'
               else:
                   next_page_clink = response.url+"&page=2"
          else:
               next_page = current_page + 1
               next_page_clink = re.sub('page=\d+','page='+str(current_page+1),response.url)
          yield  scrapy.FormRequest(next_page_clink,self.page_iterate)
