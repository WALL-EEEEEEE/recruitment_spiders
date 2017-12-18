import scrapy 

class BossJobCategoriesSpider(scrapy.Spider):
    name = 'JobCategories'
    start_urls = [ 'https://www.zhipin.com/' ]

    def parse(self,response):
        for jobcategory in response.xpath('//div[contains(@class,"sub-content")]//a'):
            job_cname = jobcategory.xpath('text()').extract();
            job_clink = jobcategory.xpath('@href').extract()
            yield {"cname":job_cname, "clink":job_clink}
