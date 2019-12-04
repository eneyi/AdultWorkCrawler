# -*- coding: utf-8 -*-
from adultwork_bot.utilities.utilities import AdultWorkSearchParameters
from adultwork_bot.utilities.engine import AdultWorkEngine
from pyquery import PyQuery
import scrapy
from scrapy.http import FormRequest, Request
from scrapy.linkextractors import LinkExtractor
from requests import get, post
from json import loads


class AdultworkSpider(scrapy.Spider):
    name = 'adultwork'
    allowed_domains = ['adultwork.com']
    #start_urls = ['http://adultwork.com/Search.asp']
    parameters = AdultWorkSearchParameters().uk_search_params()['formdata']

    #def start_request(self):
     #   #proxies = {'http': 'socks5://localhost:9050','https': 'socks5://localhost:9050'}
      #  #response = requests.post(self.start_urls[0], proxies=proxies, data=self.parameters)
       # yield FormRequest(url=self.start_urls[0], meta={"proxy": "socks5://localhost:9050"}, formdata=self.parameters, )


    ''' Start POST Request to get page 1 with UK sarch parameters'''
    def start_requests(self):
        yield FormRequest(url='http://adultwork.com/Search.asp', formdata=self.parameters, method='POST', callback=self.parse, dont_filter=True)



    '''Parse each sex worker ad on page'''
    def parse(self, response):
        pq, page = PyQuery(response.text), 1
        profileIDs = pq("a.Label[onclick*='sUF']").items()
        profileIDs = [i.attr('onclick').split('(')[-1].split(',')[0].replace(')', '') for i in profileIDs]
        print(profileIDs)
        ## for each profile id extracted, generate the sex worker's profile link
        for profileID in profileIDs:
            item = {}
            item['userid'] = profileID
            item['profile'] = 'http://adultwork.com/ViewProfile.asp?UserID={}'.format(profileID)
            item['ratingsLink'] = 'http://adultwork.com/dlgViewRatings.asp?UserID={}'.format(profileID)
            item['toursLink'] = 'http://adultwork.com/dlgUserTours.asp?UserID={}'.format(profileID)
            yield Request(url=item['profile'], callback=self.parse_profile, meta={'item': item})
        
        ## Check for next page
        hasNextPage = pq("input.Button[name='btnNext']")
        if hasNextPage:
            page += 1
            self.parameters['cboPageNo'], self.parameters['PageNo'] = str(page), str(page)
            yield FormRequest(url='http://adultwork.com/Search.asp', formdata=self.parameters, method='POST', callback=self.parse, dont_filter=True)



    '''Parse a single sex workers profile'''
    def parse_profile(self, response):
        pq, item =  PyQuery(response.text), response.meta['item']
        item = AdultWorkEngine().extract_profile(pq, item)
        yield Request(url=item['ratings']['ratingsLink'], callback=self.parse_ratings, meta = {'item': item})



    '''Parse all ratings for each sex worker on page'''
    def parse_ratings(self, response):
        item = response.meta['item']
        if item['ratings']['hasRatings']:
            pq = PyQuery(response.text)
            item = AdultWorkEngine().extract_ratings(pq, item)

        if item['reviews']['hasReviews']:
            item = AdultWorkEngine().extract_review(item)
            
            '''
            ## check for ratings page of other users on this user's ratings page
            oRatingsUrls = [i.attr('href').split('href=')[-1].replace("'", "") for i in pq('a[href*="/dlgViewRatings.asp?UserID"]').items()]
            if len(oRatingsUrls) > 0:
                for oRatingUrl in oRatingsUrls:
                    yield Request(url=oRatingUrl, callback=self.parse_ratings, meta = {'item': item})
            '''
        yield Request(url=item['tours']['tourLink'], callback=self.parse_tour, meta = {'item': item})



    '''Parse all sex worker's tours'''
    def parse_tour(self, response):
        item = response.meta['item']
        if item['tours']['hasTours']:
            pq =  PyQuery(response.text)
            item = AdultWorkEngine().extract_tours(pq, item)
        yield item
    