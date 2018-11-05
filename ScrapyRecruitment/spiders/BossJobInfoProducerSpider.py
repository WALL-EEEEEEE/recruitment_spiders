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
import redis


class BossJobInfoProducerSpider(scrapy.Spider):    
    name = 'BossJobInfoProducer'
    cities_cached_file = 'data/city.json'
    cates_cached_file='data/cate.json'
    pages_cached_file = 'data/pages.json'
    custom_settings= {
        'SCHEDULER':'scrapy.core.scheduler.Scheduler',
        'DUPEFILTER_CLASS':'scrapy.dupefilters.RFPDupeFilter'
    }
    baseurl = "https://www.zhipin.com"
    redis_name = 'BossJobInfo'
    cates = None
    cities = None

    def start_requests(self):
        init_requests = []
        # get cities 
        if not self._is_cities_cached(): 
            city_url = "https://www.zhipin.com/common/data/city.json"
            request = scrapy.FormRequest(city_url,callback=self.parse_cities,dont_filter=False,meta={'enable_proxy':False})
            init_requests.append(request)
        else:
            self._load_cities_from_cache()
            self.parse_pages()

        # get_cates
        if not self._is_cates_cached():
            index_url = "https://www.zhipin.com"
            request = scrapy.FormRequest(index_url,callback=self.parse_categories,dont_filter=False,meta={'enable_proxy':True})
            init_requests.append(request)
        else:
            self._load_cates_from_cache()
            self.parse_pages()
        return init_requests

    def _is_cities_cached(self):
        if os.path.exists(self.cities_cached_file):
             return True
        return False
    def _load_cities_from_cache(self):
        if os.access(self.cities_cached_file, os.R_OK):
            with open(self.cities_cached_file,'r') as reader:
                self.cities = json.load(reader)
        else:
            logging.error('You have not enough privillege to read from target file!')

    def _load_cates_from_cache(self):
        if os.access(self.cates_cached_file, os.R_OK):
            with open(self.cates_cached_file,'r') as reader:
                    self.cates = json.load(reader)
        else:
            logging.error('You have not enough privillege to read from target file!')

    def _is_cates_cached(self):
        if os.path.exists(self.cates_cached_file):
            return True
        return False

    def _load_pages_from_cache(self):
        if os.access(self.pages_cached_file, os.R_OK):
            tmp_pages = []
            with jsonlines.open(self.pages_cached_file,'r') as reader:
                for page in reader:
                    tmp_pages.append(page)
                self.pages = tmp_pages
        else:
            logging.error('You have not enough privillege to read from target file!')

    def _is_pages_cached(self):
        if os.path.exists(self.pages_cached_file):
             return True
        return False

    def parse_cities(self,response):
        loggging.info('parse_cities')
        def _save_as_cache(cities_data):
            target_dir =  os.path.dirname(self.cities_cached_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.access(target_dir,os.W_OK) :
                with open(self.cities_cached_file,'w') as writer:
                    json.dump(cities_data,writer)
            else:
                logging.error('You have not enough privillege to write on target file!')
        return_cities = []
        jsonize = json.loads(response.text)
        cities = jsonize.get('data',[]).get('cityList',[])
        for city in cities:
            return_cities.append({'code':city['code'],'name':city['name']})
            if city['subLevelModelList'] != None:
                for subcity in city['subLevelModelList']:
                     return_cities.append({'code':subcity['code'],'name':subcity['name']})
        _save_as_cache(return_cities)
        self.cities = return_cities
        self.parse_pages()

    def parse_categories(self,response):
        def _save_as_cache(cities_data):
            target_dir =  os.path.dirname(self.cates_cached_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.access(target_dir,os.W_OK): 
                with open(self.cates_cached_file,'w') as writer:
                    json.dump(cities_data,writer)
            else:
                logging.error('You have not enough privillege to write on target file!')

        return_cates = []
        for jobcate in response.xpath('//div[contains(@class,"menu-sub")]//a'):
            job_cname = jobcate.xpath('text()').extract();
            job_clink = jobcate.xpath('@href').extract()
            return_cates.append({'name':job_cname,'clink':job_clink})
        _save_as_cache(return_cates)
        self.cates = return_cates
        self.parse_pages()
        
    def parse_pages(self):
        urls = []
        if self.cates !=  None and  self.cities != None:
            if self._is_pages_cached():
                self._load_pages_from_cache()
            else: 
                for cate in self.cates:
                    for city in self.cities:
                         clink = self.baseurl+'/c'+str(city['code'])+cate['clink'][0]
                         urls.append(clink)
        self.feed_redis(urls)

    def feed_redis(self,start_urls):
        logging.info('Feeding start urls into redis ...')
        r = redis.StrictRedis(host='localhost',port=6379,db=0)
        start = 0
        for url in start_urls:
            logging.info('Feeding start urls inot redis ... '+str(start))
            r.lpush('BossJobInfo:start_urls',url)
            start+=1





