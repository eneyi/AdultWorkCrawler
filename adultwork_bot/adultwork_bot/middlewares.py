# -*- coding: utf-8 -*-
from toripchanger import TorIpChanger
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from adultwork_bot.utilities.tor import TorController
from adultwork_bot.utilities.utilities import Pooling
ip_changer = TorIpChanger(reuse_threshold=10)


class AdultworkBotRandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        user_agent = Pooling().ua_pool()
        request.headers['User-Agent'] = user_agent
        spider.logger.info('User Agent: %s' % request.headers['User-Agent'])



class ProxyMiddleware(object):
    _requests_count = 0

    def process_request(self, request, spider):
        self._requests_count += 1
        if self._requests_count > 10:
            self._requests_count = 0 
            ip_changer.get_new_ip()

        request.meta['proxy'] = 'http://127.0.0.1:8118'
        spider.log('Proxy : %s' % request.meta['proxy'])