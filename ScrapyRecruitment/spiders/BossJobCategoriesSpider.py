import scrapy 

class BossJobCategoriesSpider(scrapy.Spider):
    name = 'JobCategories'
    start_urls = [ 'https://www.zhipin.com/' ]

    def parse(self,response):
        for jobcate in response.xpath('//div[contains(@class,"menu-sub")]//a'):
                job_cname = jobcate.xpath('text()').extract();
                job_clink = jobcate.xpath('@href').extract()
                yield {"cname":job_cname, "clink":job_clink}
