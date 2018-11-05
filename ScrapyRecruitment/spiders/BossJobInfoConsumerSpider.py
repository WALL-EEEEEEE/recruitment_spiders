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



class BossJobInfoConsumerSpider(RedisSpider):
    name = "BossJobInfo"
    baseurl = "https://www.zhipin.com"
    job_count = 0
    page_count = 0
    pages_cached_file = 'data/pages.json'
 

    def parse(self,response):
        logging.info(response)
        def _save_as_cache(page_data):
            target_dir =  os.path.dirname(self.pages_cached_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.access(target_dir,os.W_OK) :
                    try:
                       with jsonlines.open(self.pages_cached_file,mode='w') as writer:
                           writer.write(page_data)
                    except e:
                        raise e
            else:
                logging.error('You have not enough privillege to write on target file!')

        # page_info
        logging.info(response)
        self.logger.info("Found "+ str(self.page_count)+" pages")
        last_page = response.xpath('//div[contains(@class,"page")]/a[ @ka="page-next" and contains(@class,"disabled")]');
        ensure_last_page = len(response.xpath('//div[contains(@class,"job-list")]/ul/li')) < 15;
        empty_page = len(response.xpath('//div[contains(@class,"job-list")]/ul/li')) == 0;
        current_url  = urlparse(response.url)
        page_matcher = re.match('.*page=(\d+).*',current_url.query)
        current_page = 1 if not current_url.query or (page_matcher == None) else int(page_matcher.group(1))

        if not empty_page:
            self.page_count += 1;
            _save_as_cache(current_url.geturl())
            for job_desc_page in self.parse_job_lists(response):
                 yield job_desc_page

        if not last_page and current_page < 20 and not ensure_last_page:
            if current_page == 1: 
                if not current_url.query:
                    next_page_clink = response.url+'?page=2'
                else:
                    next_page_clink = response.url+"&page=2"
            else:
                next_page = current_page + 1
                next_page_clink = re.sub('page=\d+','page='+str(current_page+1),response.url)
            yield  scrapy.FormRequest(next_page_clink,self.parse,meta={'enable_proxy':True})

    def parse_job_lists(self,Response):
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
            job_details_req = Request(job_url,callback = self.parse_job_desc,meta={'enable_proxy':True})
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
