# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    description  =  'Spiders of recruitment',
    url          =  'https://github.com/duanqiaobb/recruitment_spiders',
    author       =  'johans',
    author_email =  '2574580419@qq.com',
    license      =  'MIT',
    packages     =  find_packages(),
    install_requires = [
        'scrapy',
        'requests',
        'scrapy-redis',
        'fake_useragent'
        ]
    entry_points = {'scrapy': ['settings = ScrapyRecruitment.settings']},
)
