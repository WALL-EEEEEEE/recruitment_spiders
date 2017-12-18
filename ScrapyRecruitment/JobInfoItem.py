import scrapy
from scrapy import Item

class JobInfoItem(Item):
    job_name = scrapy.Field()
    job_url  = scrapy.Field()
    job_salary = scrapy.Field()
    job_breq  = scrapy.Field()
    job_location = scrapy.Field()
    job_year = scrapy.Field()
    job_edu  = scrapy.Field()
    company_info = { 
            'company_name':scrapy.Field(),
            'company_type':scrapy.Field(),
            'company_fstatus':scrapy.Field(),
            'company_empstatus':scrapy.Field()
            }
    

