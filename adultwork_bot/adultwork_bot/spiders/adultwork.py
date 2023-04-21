# -*- coding: utf-8 -*-
from requests import get, post
from json import loads, dumps
from pyquery import PyQuery

import scrapy
from scrapy.http import FormRequest, Request
from scrapy.linkextractors import LinkExtractor

from adultwork_bot.utilities.utilities import AdultWorkSearchParameters
from adultwork_bot.utilities.engine import AdultWorkEngine
from adultwork_bot.utilities.updater import AdultworkProfileUpdate
from adultwork_bot.pipelines import AdultworkMongoPipeline as amp


class AdultworkSpider(scrapy.Spider):
    name = 'adultwork'
    allowed_domains = ['adultwork.com']
    start_urls = ['http://adultwork.com/Search.asp']
    parameters = AdultWorkSearchParameters().uk_search_params()['formdata']

    db = amp('Adultwork').connect_db()
    itemcount = 0


    ''' Start POST Request to get page 1 with UK search parameters'''
    def parse(self, response):
        yield FormRequest(url=response.url, formdata=self.parameters, method='POST', callback=self.parse_ids)


    '''Parse each sex worker ad on page'''
    def parse_ids(self, response):
        pq = PyQuery(response.text)
        profileIDs = pq("a.Label[onclick*='sUF']").items()
        profileIDs = [i.attr('onclick').split('(')[-1].split(',')[0].replace(')', '') for i in profileIDs]
        profileIDs = list(set(profileIDs))
        print(len(profileIDs))
        print(self.parameters['PageNo'])

        ## for each profile id extracted, generate the sex worker's profile link
        for profileID in profileIDs:
            item = {}
            self.itemcount += 1
            item['profile'] = {}
            item['userid'] = profileID
            item['profile']['scrapejob'] = self.itemcount
            item['profile']['profilelink'] = 'http://adultwork.com/ViewProfile.asp?UserID={}'.format(profileID)
            '''
            if int(self.db.profiles.find({'userid': profileID}).count()) == 0:
                print('User profile for {} found; running update.......'.format(profileID))
                item['update'] = True
                continue
            '''

            print('User profile for {} found; starting scrape job.......'.format(profileID))
            item['update'] = False
            yield Request(url=item['profile']['profilelink'], callback=self.parse_profile, meta={'item': item})

        ## Check for next page
        #hasNextPage = pq("input.Button[name='btnNext']")
        lastPage, page = 1153, int(self.parameters['PageNo'])
        #if hasNextPage:
        if page < lastPage:
            page += 1
            #item['profile']['page'] = page
            self.parameters['PageNo'] = str(page)
            self.parameters['cboPageNo'] = str(page)
            self.parameters['btnNext'] = '>'
            yield FormRequest.from_response(response, formdata=self.parameters, formname='frmSearch', callback=self.parse_ids, dont_filter=True)


    '''Parse a single sex workers profile'''
    def parse_profile(self, response):

        pq, item = PyQuery(response.text), response.meta['item']
        updater = response.meta['item']['update']

        profileID = item['userid']
        print('Parsing profile for {} .......'.format(profileID))
        item['profile']['userid'] = profileID
        item['profile']['ratingsLink'] = 'http://adultwork.com/dlgViewRatings.asp?UserID={}'.format(profileID)
        item['profile']['blogLink'] = 'https://www.adultwork.com/Blog.asp?UserID={}'.format(profileID)
        item['profile']['galleryLink'] = 'https://www.adultwork.com/Gallery.asp?UserID={}'.format(profileID)
        item['toursLink'] = 'http://adultwork.com/dlgUserTours.asp?UserID={}'.format(profileID)

        if updater:
            AdultworkProfileUpdate(item['userid']).update_location(pq=pq, userid=profileID)
            AdultworkProfileUpdate(item['userid']).update_logins(pq=pq, userid=profileID)
        else:
            print('Scraping profile for {}'.format(item['profile']['userid']))
            item = AdultWorkEngine().extract_profile(pq, item)
            yield Request(url=item['profile']['toursLink'], callback=self.parse_tour, meta = {'item': item})


    '''Parse all sex worker's tours'''
    def parse_tour(self, response):
        item = response.meta['item']
        if item['profile']['hasTours']:
            print('Parsing tours for {} .......'.format(item['profile']['userid']))
            print('Scraping tours for {}'.format(item['profile']['userid']))
            pq = PyQuery(response.text)
            item = AdultWorkEngine().extract_tours(pq, item)
        yield Request(url=item['profile']['ratingsLink'], callback=self.parse_ratings, meta = {'item': item})


    '''Parse all ratings for each sex worker on page'''
    def parse_ratings(self, response):
        item = response.meta['item']
        if item['profile']['hasRatings']:
            print('Scraping ratings for {}'.format(item['profile']['userid']))
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
            print('Scraping reviews for {}'.format(item['profile']['userid']))
            item = AdultWorkEngine().extract_reviews(item)
        yield item
        print('\n\n\n\n\n\n Finished profile for {}'.format(item['profile']['userid']))
