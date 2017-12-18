# Retry when proxies fail
RETRY_TIMES = 3

# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500,503,504,400,403,404,408]

DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware':80,
        'ScrapyRecruitment.ProxyMiddleware.ProxyMiddleware':90,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware':100,
        }
