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


class BossJobInfoSpider(scrapy.Spider):
    name = "BossJobInfo"
    baseurl = "https://www.zhipin.com"
    job_count = 0


    def get_city_list(self):
        save_file = 'data/city.json'

        def _parse_cities(response):
            jsonize = json.loads(response.text)
            cities = []
            return_cities = []
            if jsonize != None:
                cities = jsonize.get('data',[]).get('cityList',[])
            for city in cities:
                return_cities.append({'code':city['code'],'name':city['name']})
                if city['subLevelModelList'] != None:
                    for subcity in city['subLevelModelList']:
                        return_cities.append({'code':subcity['code'],'name':subcity['name']})
            _save_as_cache(return_cities)
            self.cities = return_cities

        def _save_as_cache(cities_data):
            target_dir =  os.path.dirname(save_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.access(target_dir,os.W_OK) :
                with open(save_file,'w') as writer:
                    json.dump(cities_data,writer)
            else:
                logging.error('You have not enough privillege to write on target file!')
        def _load_from_cache():
            if os.access(save_file, os.R_OK):
                with open(save_file,'r') as reader:
                    self.cities = json.load(reader)
            else:
                logging.error('You have not enough privillege to read from target file!')
        def _is_cached():
            if os.path.exists(save_file):
                return True
            return False
                
        if _is_cached():
            _load_from_cache()
            request = []
        else: 
            city_url = "https://www.zhipin.com/common/data/city.json"
            request = scrapy.FormRequest(city_url,callback=_parse_cities,dont_filter=False,meta={'enable_proxy':True})
        return request

    def get_category_list(self):
        save_file = 'data/cate.json'

        def _parse_categories(response):
            return_cates = []
            for jobcate in response.xpath('//div[contains(@class,"menu-sub")]//a'):
                job_cname = jobcate.xpath('text()').extract();
                job_clink = jobcate.xpath('@href').extract()
                return_cates.append({'name':job_cname,'clink':job_clink})
            _save_as_cache(return_cates)
            self.cates = return_cates


        def _save_as_cache(cities_data):
            target_dir =  os.path.dirname(save_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.access(target_dir,os.W_OK): 
                with open(save_file,'w') as writer:
                    json.dump(cities_data,writer)
            else:
                logging.error('You have not enough privillege to write on target file!')
        def _load_from_cache():
            if os.access(save_file, os.R_OK):
                with open(save_file,'r') as reader:
                    self.cates = json.load(reader)
            else:
                logging.error('You have not enough privillege to read from target file!')

        def _is_cached():
            if os.path.exists(save_file):
                return True
            return False
 
        if _is_cached():
            _load_from_cache()
            request = []
        else: 
            index_url = "https://www.zhipin.com"
            request = scrapy.FormRequest(index_url,callback=_parse_categories,dont_filter=False,meta={'enable_proxy':True})
 
        return request

    def get_page_list(self):
        save_file = 'data/pages.json'
        self.page_count = 0
        self.jsonline_writer = None

        def _parse_pages(response):
             # page_info
             logging.info(response)
             self.logger.info("Found "+ str(self.page_count)+" pages")
             last_page = response.xpath('//div[contains(@class,"page")]/a[ @ka="page-next" and contains(@class,"disabled")]');
             ensure_last_page = len(response.xpath('//div[contains(@class,"job-list")]/ul/li')) < 15;
             empty_page = len(response.xpath('//div[contains(@class,"job-list")]/ul/li')) == 0;
             current_url  = urlparse(response.url)
             if not empty_page:
                 self.page_count += 1;
                 _save_as_cache(current_url.geturl())
             page_matcher = re.match('.*page=(\d+).*',current_url.query)
             current_page = 1 if not current_url.query or (page_matcher == None) else int(page_matcher.group(1))

             if not last_page and current_page < 20 and not ensure_last_page:
                 if current_page == 1: 
                     if not current_url.query:
                         next_page_clink = response.url+'?page=2'
                     else:
                         next_page_clink = response.url+"&page=2"
                 else:
                     next_page = current_page + 1
                     next_page_clink = re.sub('page=\d+','page='+str(current_page+1),response.url)
                 yield  scrapy.FormRequest(next_page_clink,_parse_pages,dont_filter=True,meta={'enable_proxy':True})

        def _save_as_cache(page_data):
            target_dir =  os.path.dirname(save_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.access(target_dir,os.W_OK) :
                if self.jsonline_writer == None:
                    try:
                       self.jsonline_writer =  jsonlines.open(save_file,mode='w')
                       self.jsonline_writer.write(page_data)
                    except e:
                        raise e
                else:
                    self.jsonline_writer.write(page_data)
            else:
                logging.error('You have not enough privillege to write on target file!')

        def _load_from_cache():
            if os.access(save_file, os.R_OK):
                tmp_pages = []
                with jsonlines.open(save_file,'r') as reader:
                    for page in reader:
                        tmp_pages.append(page)
                self.pages = tmp_pages
            else:
                logging.error('You have not enough privillege to read from target file!')

        def _is_cached():
            if os.path.exists(save_file):
                return True
            return False
 

        request = []
        if _is_cached():
            _load_from_cache()
        else: 
            for cate in self.cates:
                for city in self.cities:
                     clink = self.baseurl+'/c'+str(city['code'])+cate['clink'][0]
                     crequest = scrapy.FormRequest(clink,_parse_pages,dont_filter=True,meta={'enable_proxy':True})
                     request.append(crequest)
        return request

    def start_requests(self):

        #load the cities list
        yield self.get_city_list()
        #load the categories list
        yield self.get_category_list()
        #load pagelist
        for request in self.get_page_list():
            yield request

        """
        os._exit(0)
        crequests = []
        with jsonlines.open('./data/BossJobPages2.jl') as reader:
            for list_url in reader:
                clink = list_url['page_url']
                crequest = scrapy.FormRequest(clink)
                crequests.append(crequest)
        return crequests
        """
    def parse(self,Response):
        """ extract the job info """ 
        job_list = Response.xpath('//div[contains(@class,"job-list")]/ul/li');
        for jobinfo in job_list:
            #Get job name
            job_name = jobinfo.xpath('div[contains(@class,"job-primary")]/div[contains(@class,"info-primary")]/h3/a/text()').extract();
            #Get job url
            job_url  = self.baseurl+jobinfo.xpath('div[contains(@class,"job-primary")]/div[contains(@class,"info-primary")]/h3/a/@href').extract_first();
            #Get job salary 
            job_salary = jobinfo.xpath('div[contains(@class,"job-primary")]/div[contains(@class,"info-primary")]/h3/a/span/text()').extract();
            #Get job location
            job_breq = jobinfo.xpath('div[contains(@class,"job-primary")]/div[contains(@class,"info-primary")]/p/text()').extract();
            job_location = job_breq[0]
            job_year = job_breq[1]
            job_edu  = job_breq[2]
            #Get company info
            company_name = jobinfo.xpath('div[contains(@class,"job-primary")]/div[contains(@class,"info-company")]/div/h3/a/text()').extract()
            company_info = jobinfo.xpath('div[contains(@class,"job-primary")]/div[contains(@class,"info-company")]/div/p/text()').extract()

            company_type =  company_info[0] if len(company_info) > 0  else '';
            company_fstatus = company_info[1]  if len(company_info) > 1 else '';
            company_empstatus = company_info[2] if len(company_info) > 2 else '';

            job_company = [
                    ('name', company_name),
                    ('type', company_type),
                    ('fstatus',company_fstatus),
                    ('empstatus',company_empstatus)
            ]
            job_tags = jobinfo.xpath('div[contains(@class,"job-tags")]/span/text()').extract()
            job_info = {'job_name':job_name,'job_url':job_url,'job_salary':job_salary,'job_location':job_location,'job_year':job_year,'job_edu':job_edu,
                    'job_company':job_company
                    }
            job_details_req = Request(job_url,callback = self.parse_job_desc)
            job_details_req.meta['job_info'] = job_info
            yield job_details_req
    def parse_job_desc(self,response):
        """Parse the job details"""
        job_info = response.meta['job_info']
        job_desc = response.xpath('//div[contains(@class,"job-sec")]/div[contains(@class,"text")]/text()').extract()
        job_comloc = response.xpath('//div[contains(@class,"location-address")]/text()').extract()
        job_info['job_desc'] = ''.join(str(desc) for desc in job_desc)
        job_info['job_location_detail'] = job_comloc
        self.job_count += 1;
        self.logger.info("Found "+str(self.job_count)+" jobs ...")
        yield job_info




