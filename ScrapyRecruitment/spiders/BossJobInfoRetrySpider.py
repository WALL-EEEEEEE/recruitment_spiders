import scrapy
import json
import sys
import os
from scrapy import Request
from scrapy import signals
import jsonlines

class BossJobInfoSpider(scrapy.Spider):
    name = "JobInfo"
    baseurl = "https://www.zhipin.com"
    job_count = 0
    def start_requests(self):
        #load the categories list
        crequests = []
        with jsonlines.open('./data/BossJobInfosRetried2.jl') as reader:
            for list_url in reader:
                clink = list_url['page_url']
                crequest = scrapy.FormRequest(clink)
                crequests.append(crequest)
        return crequests

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




