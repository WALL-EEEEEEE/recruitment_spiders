
from scrapy import Spider

class BossCityList(Spider):

    name = "BossCitiList"
    allowed_domains = [ "www.zhipin.com" ]
    start_urls = [ 'https://www.zhipin.com/' ]

    def parse(self,response):
        cityLists = response.xpath('//div[contains(@class,"dorpdown-city")]/ul[ not(contains(@class, "show"))]/li')
        for city in cityLists:
            cityCode = city.xpath('@data-val').extract_first()
            cityName = city.xpath('text()').extract_first()
            yield {'cityCode':cityCode, 'cityName':cityName}


