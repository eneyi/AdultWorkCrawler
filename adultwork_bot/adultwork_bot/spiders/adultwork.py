# -*- coding: utf-8 -*-
from adultwork_bot.utilities.utilities import AdultWorkSearchParameters
from adultwork_bot.utilities.engine import AdultWorkEngine
from pyquery import PyQuery
import scrapy
from scrapy.http import FormRequest, Request
from scrapy.linkextractors import LinkExtractor
from requests import get, post
from json import loads, dumps
from adultwork_bot.utilities.utilities import db


class AdultworkSpider(scrapy.Spider):
    name = 'adultwork'
    allowed_domains = ['adultwork.com']
    parameters = AdultWorkSearchParameters().uk_search_params()['formdata']

    ##get list of already scraped profiles
    database = db().connect_mongo(database='Adultwork')
    scraped_ids = [i['userid'].strip() for i in database['profiles'].find()]


    ''' Start POST Request to get page 1 with UK sarch parameters'''
    def start_requests(self):
        yield FormRequest(url='http://adultwork.com/Search.asp', formdata=self.parameters, method='POST', callback=self.parse, dont_filter=True)



    '''Parse each sex worker ad on page'''
    def parse(self, response):
        pq = PyQuery(response.text)
        profileIDs = pq("a.Label[onclick*='sUF']").items()
        profileIDs = [i.attr('onclick').split('(')[-1].split(',')[0].replace(')', '') for i in profileIDs]

        ## for each profile id extracted, generate the sex worker's profile link
        for profileID in profileIDs:
            if profileID in self.scraped_ids:
                print('User profile for {} found; running update.......'.format(profileID))
                pass
            else:
                print('User profile for {} not found; initiating scrape job........'.format(profileID))
                item = {}
                item['profile'] = {}
                item['profile']['userid'] = profileID
                item['profile']['profilelink'] = 'http://adultwork.com/ViewProfile.asp?UserID={}'.format(profileID)
                item['profile']['ratingsLink'] = 'http://adultwork.com/dlgViewRatings.asp?UserID={}'.format(profileID)
                item['toursLink'] = 'http://adultwork.com/dlgUserTours.asp?UserID={}'.format(profileID)
                yield Request(url=item['profile']['profilelink'], callback=self.parse_profile, meta={'item': item})

                ## Check for next page
                hasNextPage = pq("input.Button[name='btnNext']")
                if hasNextPage:
                    page = int(self.parameters['PageNo'])
                    page += 1
                    self.parameters['PageNo'] = str(page)
                    self.parameters['cboPageNo'] = str(page)
                    self.parameters['btnNext'] = '>'
                    yield FormRequest.from_response(response, formdata=self.parameters, formname='frmSearch', callback=self.parse, dont_filter=True)


    '''Parse a single sex workers profile'''
    def parse_profile(self, response):
        pq, item =  PyQuery(response.text), response.meta['item']
        item = AdultWorkEngine().extract_profile(pq, item)
        yield Request(url=item['profile']['tourLink'], callback=self.parse_tour, meta = {'item': item})

    '''Parse all sex worker's tours'''
    def parse_tour(self, response):
        item = response.meta['item']
        if item['profile']['hasTours']:
            pq =  PyQuery(response.text)
            item = AdultWorkEngine().extract_tours(pq, item)
        yield Request(url=item['profile']['ratingsLink'], callback=self.parse_ratings, meta = {'item': item})

    '''Parse all ratings for each sex worker on page'''
    def parse_ratings(self, response):
        item = response.meta['item']
        if item['profile']['hasRatings']:
            
            pq = PyQuery(response.text)
            item = AdultWorkEngine().extract_ratings(pq, item)

            '''
            ## check for ratings page of other users on this user's ratings page
            oRatingsUrls = [i.attr('href').split('href=')[-1].replace("'", "") for i in pq('a[href*="/dlgViewRatings.asp?UserID"]').items()]
            if len(oRatingsUrls) > 0:
                for oRatingUrl in oRatingsUrls:
                    yield Request(url=oRatingUrl, callback=self.parse_ratings, meta = {'item': item})
            '''

        if item['profile']['hasReviews']:
            item['reviews']['reviews'] = []
            item = AdultWorkEngine().extract_review(item)
        yield item



    
    