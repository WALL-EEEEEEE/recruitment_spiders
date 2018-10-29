BOT_NAME= "ScrapyRecruitment"
SPIDER_MODULES="ScrapyRecruitment.spiders"
# Retry when proxies fail
RETRY_TIMES = 3
# Disable ROBOTSTXT_OBEY
ROBOTSTXT_OBEY=False
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500,503,504,400,403,404,408]

DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware':None,
        'ScrapyRecruitment.RetryMiddleware.RetryMiddleware':80,
        'ScrapyRecruitment.ProxyMiddleware.ProxyMiddleware':90,
        'ScrapyRecruitment.FakerUserAgentMiddleware.FakerUserAgentMiddleware':89,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware':100,
        }
