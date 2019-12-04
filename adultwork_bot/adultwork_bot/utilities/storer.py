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
    start_urls = ['http://adultwork.com/Search.asp']
    parameters = AdultWorkSearchParameters().uk_search_params()['formdata']

    #def start_request(self):
     #   #proxies = {'http': 'socks5://localhost:9050','https': 'socks5://localhost:9050'}
      #  #response = requests.post(self.start_urls[0], proxies=proxies, data=self.parameters)
       # yield FormRequest(url=self.start_urls[0], meta={"proxy": "socks5://localhost:9050"}, formdata=self.parameters, )


    ''' Start POST Request to get page 1 with UK sarch parameters'''
    def parse(self, response):
        #params = {"formdata":{"cboCountryID":"158","cboRegionID":"0","cboCountyID":"0","strTown":"","cboNationalityID":"0","rdoNationalityInclude":"1","cboSCID":"0","cboAPID":"0","strKeywords":"","rdoKeySearch":"1","cboLastLoginSince":"X","strSelUsername":"","intAgeFrom":"","intAgeTo":"","rdoOrderBy":"1","rdoRatings":"0","question_1":"(select)","question_69":"","question_70":"","question_84":"","question_2":"","question_3":"","question_4":"(select)","question_5":"(select)","question_57":"","question_7":"(select)","question_8":"(select)","question_9":"(select)","question_10":"(select)","question_82":"(select)","GC_11":"(select)","question_11":"(select)","GC_46":"(select)","question_46":"(select)","GC_47":"(select)","question_47":"(select)","GC_58":"(select)","question_58":"(select)","GC_12":"(select)","question_12":"(select)","question_13":"(select)","GC_80":"(select)","question_80":"(select)","question_81":"(select)","question_14":"(select)","question_67":"(select)","question_49":"(select)","question_27":"","question_42":"","dteMeetDate":"","dteMeetTime":"X","intMeetDuration":"","intMeetPrice":"","cboBookingCurrencyID":"28","intHalfHourRateFrom":"","intHalfHourRateTo":"","intHourlyRateFrom":"","intHourlyRateTo":"","intOvernightRateFrom":"","intOvernightRateTo":"","dteAvailableAnotherDay":"","intMiles":"","strSelPostCode":"","strPostCodeArea":"","cboLastUpdated":"01/01/2003","intHotListID":"0","CommandID":"2","PageNo":"1","HotListSearch":"0","SearchTab":"Profile","hdteToday":"04/12/2019","DF":"1","SS":"0"}}
        yield FormRequest(url='http://adultwork.com/Search.asp', formdata=self.parameters, method='POST', callback=self.parse_pages, dont_filter=True)


    '''Parse each sex worker ad on page'''
    def parse_pages(self, response):
        pq, page = PyQuery(response.text), 1
        profileIDs = pq("a.Label[onclick*='sUF']").items()
        profileIDs = [i.attr('onclick').split('(')[-1].split(',')[0].replace(')', '') for i in profileIDs]
        item = {}
        ## for each profile id extracted, generate the sex worker's profile link
        for profileID in profileIDs:
            item['userid'] = profileID
            item['profile'] = 'http://adultwork.com/ViewProfile.asp?UserID={}'.format(profileID)
            item['ratingsLink'] = 'http://adultwork.com/dlgViewRatings.asp?UserID={}'.format(profileID)
            item['toursLink'] = 'http://adultwork.com/dlgUserTours.asp?UserID={}'.format(profileID)
            yield Request(url=item.get('profile'), callback=self.parse_profile, meta={'item': item})
        '''
        ## Check for next page
        hasNextPage = pq("input.Button[name='btnNext']")
        if hasNextPage:
            page += 1
            self.parameters['cboPageNo'], self.parameters['PageNo'] = str(page), str(page)
            yield FormRequest(url='http://adultwork.com/Search.asp', formdata=self.parameters, method='POST', callback=self.parse, dont_filter=True)
        '''

            

    '''Parse a single sex workers profile'''
    def parse_profile(self, response):
        pq, item =  PyQuery(response.text), response.meta['item']
        item = AdultWorkEngine().extract_profile(pq, item)
        yield item
        #yield Request(url=item['ratings']['ratingsLink'], callback=self.parse_ratings, meta = {'item': item})


    '''Parse all ratings for each sex worker on page'''
    def parse_ratings(self, response):
        item = response.meta['item']
        if item['ratings']['hasRatings']:
            pq = PyQuery(response.text)
            item = AdultWorkEngine().extract_ratings(pq, item)
            
            '''
            ## check for ratings page of other users on this user's ratings page
            oRatingsUrls = [i.attr('href').split('href=')[-1].replace("'", "") for i in pq('a[href*="/dlgViewRatings.asp?UserID"]').items()]
            if len(oRatingsUrls) > 0:
                for oRatingUrl in oRatingsUrls:
                    yield Request(url=oRatingUrl, callback=self.parse_ratings, meta = {'item': item})
            '''
        yield item

    '''Parse all reviews for each sex worker on page'''
    def parse_review(self, response):
        item, pq = response.meta['item'], PyQuery(response.text)
        item = AdultWorkEngine().extract_review(pq, item)
        yield item

    '''Parse all sex worker's tours'''
    def parse_tour(self, response):
        item, pq = response.meta['item'], PyQuery(response.text)
        item = AdultWorkEngine().extract_tours(pq, item)
        yield item
