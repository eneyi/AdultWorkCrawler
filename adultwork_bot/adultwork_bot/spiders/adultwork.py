# -*- coding: utf-8 -*-
from adultwork.utilities.utilities import SearchParameters
from adultwork.utilities.engine import AdultworkEngine
from pyquery import PyQuery
import scrapy
from scrapy.http import FormRequest, Request
from scrapy.linkextractors import LinkExtractor



class AdultworkSpider(scrapy.Spider):
    name = 'adultwork'
    allowed_domains = ['adultwork.com']
    base_url = 'https://www.adultwork.com/Search.asp'
    parameters = SearchParameters.uk_search_params()['formdata']


    ''' Start POST Request to get page 1 with UK sarch parameters'''
    def start_requests(self):
        return FormRequest(self.base_url, formdata=self.parameters, callback=self.parse)


    '''Parse each sex worker ad on page'''
    def parse(self, response):
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
            self.start_requests()


    '''Parse a single sex workers profile'''
    def parse_profile(self, response):
        pq, item =  PyQuery(response.text), response.meta['item']
        item = AdultworkEngine().extract_profile(pq, item)
        ## if field report is present, parse reviews
        yield Request(url=item['ratings']['ratingsLink'], callback=self.parse_ratings, meta = {'item': item})

    '''Parse all ratings for each sex worker on page'''
    def parse_ratings(self, response):
        item, stored_ratings = response.meta['item'], db.connect()['ratings'].findall('userid')

        if item['ratings']['hasRatings'] and item['ratings']['userid'] not in stored_ratings:
            item['userid']['ratings']
            pq = PyQuery(response.text)
            item = AdultworkEngine().extract_ratings(pq, item)
            oRatingsUrls = [i.attr('href').split('href=')[-1].replace("'", "") for i in pq('a[href*="/dlgViewRatings.asp?UserID"]').items()]
            if len(oRatingsUrls) > 0:
                for oRatingUrl in oRatingsUrls:
                    yield Request(url=oRatingUrl, callback=self.parse_ratings, meta = {'item': item})
        else:
            pass
        yield Request(url=item.get('reviewsLink'), callback=self.parse_reviews, meta = {'item': item})

    
    '''Parse all reviews for each sex worker on page'''
    def parse_reviews(self, response):
        pass

    '''Parse all sex worker's tours'''
    def parse_tours(self, response):
        item, res = response.meta['item'], response.text
        item['tours']
        pass
