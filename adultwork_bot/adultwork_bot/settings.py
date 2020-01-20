# -*- coding: utf-8 -*-
from adultwork_bot.utilities.utilities import Pooling

# Scrapy settings for adultwork_bot project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'adultwork_bot'

SPIDER_MODULES = ['adultwork_bot.spiders']
NEWSPIDER_MODULE = 'adultwork_bot.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16
MONGO_DB = 'Adultwork'
SQL_DB = 'adultwork'

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False


# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'adultwork_bot.middlewares.AdultworkBotSpiderMiddleware': 543,
#}

#DOWNLOADER_MIDDLEWARES = {
#    'adultwork_bot.middlewares.AdultworkBotDownloaderMiddleware': 543,
#}

DOWNLOADER_MIDDLEWARES = {
    #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    #'adultwork_bot.middlewares.ProxyMiddleware': 100,
    #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

#ROTATING_PROXY_LIST_PATH = '/home/ssori/Github/awbot/adultwork_bot/adultwork_bot/utilities/proxies.txt'
#ROTATING_PROXY_LIST = Pooling().proxy_pool()
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'adultwork_bot.pipelines.AdultworkCleanerPipeline': 300,
    'adultwork_bot.pipelines.AdultworkMongoPipeline': 310,
    }
