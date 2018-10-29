
from scrapy import Spider
import logging

class BossCityList(Spider):

    name = "BossCityList"
    allowed_domains = [ "www.zhipin.com" ]
    start_urls = [ 'https://www.zhipin.com/common/data/city.json' ]

    def parse(self,response):
        logging.info(response.text)
