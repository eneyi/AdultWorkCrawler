# -*- coding: utf-8 -*-
from adultwork_bot.utilities.utilities import AdultWorkSearchParameters
from adultwork_bot.utilities.engine import AdultWorkEngine
from pyquery import PyQuery
import scrapy
from scrapy.http import FormRequest, Request
from scrapy.linkextractors import LinkExtractor


class AdultworkSpider(scrapy.Spider):
    name = 'adultwork'
    allowed_domains = ['adultwork.com']
    start_urls = ['https://www.adultwork.com/Search.asp']
    parameters = AdultWorkSearchParameters().uk_search_params()['formdata']


    ''' Start POST Request to get page 1 with UK sarch parameters'''
    '''Parse each sex worker ad on page'''
    def parse(self, response):
        return FormRequest.from_response(response, formdata=self.parameters, callback=self.parse_pages)
    
    def parse_pages(self, response):
        pq, page = PyQuery(response.text), 1
        profileIDs = pq("a.Label[href*='javascript:vG']").items()
        profileIDs = [i.attr('href').split('(').replace(')', '') for i in profileIDs]
        item = {}
        ## for each profile id extracted, generate the sex worker's profile link
        for profileID in profileIDs:
            item['userid'] = profileID
            item['profile'] = 'https://www.adultwork.com/ViewProfile.asp?UserID={}'.format(profileID)
            item['ratingsLink'] = 'https://www.adultwork.com/dlgViewRatings.asp?UserID={}'.format(profileID)
            item['toursLink'] = 'https://www.adultwork.com/dlgUserTours.asp?UserID={}'.format(profileID)
            yield Request(url=item.get('profile'), callback=self.parse_profile, meta={'item': item})
        
        ## Check for next page
        hasNextPage = pq("input.Button[name='btnNext']")
        if hasNextPage:
            page += 1
            self.parameters['cboPageNo'], self.parameters['PageNo'] = str(page), str(page)
            yield Request(url=response.url, callback=self.parse)
            

    '''Parse a single sex workers profile'''
    def parse_profile(self, response):
        pq, item =  PyQuery(response.text), response.meta['item']
        item = AdultWorkEngine().extract_profile(pq, item)
        yield item  
