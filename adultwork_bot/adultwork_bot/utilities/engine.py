''' This handles the extraction of data from pyquery objects for each data item '''

import string, phonenumbers, requests, mapbox
from pyquery import PyQuery
from time import sleep
from twilio.rest import Client
from datetime import datetime
from pymongo import MongoClient
from adultwork_bot.pipelines import AdultworkBotCleanerPipeline as acp


'''This class is a profile updater for adult work, will update profiles for workers already captured'''
class AdultworkProfileUpdate(object):
    def __init__(self , userid):
        self.description = 'This class handles the update of fields Logins, date:location'
        self.userid = userid

    def connect_db(self):
        client = MongoClient(host = 'localhost', port = 27017)
        return client

    def update_location(self, pq):

        conn = self.connect_db()
        db = conn.Adultwork

        db_obj = db.profiles.find_one({'userid': self.userid})
        currentLocation = AdultWorkEngine().get_location(pq)
        previousLocation = db_obj['location']

        if currentLocation == previousLocation:
            pass

        else:
            print('Detected Location Change For {}. Updating Location Tracker.....'.format(self.userid))
            phone = pq('b[itemprop="telephone"]').text()
            anonp = AdultWorkEngine().anonymize_phone(phone)

            if db.phones.find_one({'number': anonp}):
                db.phones.insert(AdultWorkEngine().get_phone(phone))

            db.trackers.insert({datetime.today().strftime('%Y-%m-%d') : currentLocation, 'userid': self.userid, 'phone': anonp})
            db.profiles.update({'userid': self.userid}, {'$set': {'location': currentLocation}})
        conn.close()

    def update_phone(self, pq):
        return 0

    def update_logins(self, pq):
        conn = self.connect_db()
        db = conn.Adultwork

        db_obj = db.profiles.find_one({'userid': self.userid})
        pll = db_obj['lastLogin']
        last_available = db_obj['availabilty']
        current_available = AdultWorkEngine().self.get_availability(pq)
        cll = acp().process_last_login(pq('td.Label:contains("Last Login:")').next().text())

        if cll != pll:
            print('Detected new login details for {}...'.format(self.userid))
            db.logins.insert({'userid': self.userid, 'loggedin': cll})

        conn.close()

    def update_tours(self, pq):
        return 0


class AdultWorkEngine(object):
    def __init__(self):
        self.description = 'This class handle the extraction of data from pyquery objects for each data item'
        self.twilio_acid = 'ACc8054c3efafaed2c088987ccff19ef36' #account id
        self.twilio_token = '4d32fb02013e925c18e88c0d679aeb1c' #account token
        self.twilio_client = Client(self.twilio_acid, self.twilio_token)
        self.mapbox_token = 'pk.eyJ1IjoiZW5ueWVubnkiLCJhIjoiY2s1ZWZyZW9jMDA3MDNybnd6emQ1dGM2NSJ9.m3izYQUdHEhkK07O3Xz-oA'
        self.mapbox_client = mapbox.Geocoder(access_token=self.mapbox_token)

    '''Anonymizes phone numbers'''
    def anonymize_phone(self, phone):
        letters = string.ascii_lowercase
        phone = ''.join([letters[int(i)] for i in phone.split('+')[-1]])
        return phone

    '''Geolocate String Addresses'''
    def get_lat_long(self, address):
        g = self.mapbox_client.forward(address)
        if g.status_code == 200:
            try:
                j = g.json()['features'][0]['geometry']['coordinates']
            except:
                j= None
        return j

    '''Extracts phone/contact data fields from pyquery object-pq and stores in data object - item '''
    def get_phone(self, phone):
        data = {}
        pn = self.twilio_client.lookups.phone_numbers(phone).fetch(type='carrier')
        data['number'] = self.anonymize_phone(phone)
        data['stemmed'] = data['number'][:-1]
        data['country_code'] = pn.country_code
        data['carrier'] = pn.carrier['name']
        data['phone_type'] = pn.carrier['type']
        data['linked_profiles'] = 1
        return data

    '''Get availability'''
    def get_availability(self, pq):
        available_today = 'Available Today' in pq
        return available_today

    '''Get Polls'''
    def get_user_polls(self, pq):
        hasPolls = 'Poll.asp?PollID=' in pq
        if hasPolls:
            polls = []
            pollsLinks = pq('a[href*="Poll.asp?PollID="]').items()
            for poll in pollsLinks:
                data = {}
                link = poll.attr('href')
                data['pollId'] = link.split('PollID=')[-1].split('&')[0]
                data['poolLink'] = 'https://www.adultwork.com/Poll.asp?PollID={}'.format(data['pollid'])
                data['pollTitle'] = poll.attr('title').strip()
                polls.append(data)
            return polls

    '''Get user socials'''
    def get_user_social(self, pq):
        #€#use user id 549295 as sample
        hasLinks = ''
        if hasLinks:
            data = {}
            facebook = pq('')
            twitter = pq('')
            instagram = pq('')
            website = pq('')
        return 0

    '''Extracts location data fields from pyquery object-pq and stores in data object - item '''
    def get_location(self, pq):
        data = {}
        ## Location Data
        data['town'] = pq('td.Label:contains("Town")').next().text()
        data['county'] = pq('td.Label:contains("County")').next().text()
        data['region'] = pq('td.Label:contains("Region")').next().text()
        data['country'] = pq('td.Label:contains("Country")').next().text()
        data['coordinates'] = self.get_lat_long('{}, {}, {}, {}'.format(data['town'], data['county'], data['region'], data['country']))
        print(data['coordinates'])
        return data

    '''Extracts demographics data fields from pyquery object-pq and stores in data object - item '''
    def get_demographics(self, pq):
        data = {}
        data['nationality'] = pq('td.Label:contains("Nationality")').next().text()
        data['gender'] = pq('td.Label:contains("Gender")').next().text()
        data['orientation'] = pq('td.Label:contains("Orientation")').next().text()
        data['age'] = pq('td.Label:contains("Age")').next().text()
        data['ethnicity'] = pq('td:contains("Ethnicity:")').next().text()
        data['dressSize'] = pq('td:contains("Dress Size:")').next().text()
        data['height'] = pq('td:contains("Height:")').next().text()
        data['chestSize'] = pq('td:contains("Chest Size:")').next().text()
        data['hairColor'] = pq('td:contains("Hair Colour:")').next().text()
        data['eyeColor'] = pq('td:contains("Eye Colour:")').next().text()
        return data

    '''Extracts services data fields from pyquery object-pq and stores in data object - item '''
    def get_services(self, pq):
        data = {}
        data['escort'] = 'escort' in pq('a[href*="javascript:makeBooking()"]').text().lower()
        data['incall'] = pq('')
        data['outcall'] = pq('')
        data['phoneChat'] = 'phone chat' in pq('a[href*="javascript:doPhoneChat()"]').text().lower()
        data['smsChat'] = 'sms chat' in pq('a[href*="javascript:doSMSChat()"]').text().lower()
        data['webcam'] = 'webcam' in pq('a[href*="javascript:dC"]').text().lower()
        data['massage'] = 'massage' in pq('#main-content-container').text().lower().lower()
        ats = pq('.ToolTip:contains("Alternative")').attr("title")
        data['alternatives'] = [i for i in ats.replace('\r', '').split('\n')[1::] if i != ''] if ats else []
        data['tolet'] = 'to let' in pq('td:contains("Other Services")').text().lower()
        data['masseurs'] = 'masseur' in pq('td:contains("Other Services")').text().lower()
        data['seekingModels'] = 'models wanted' in pq('td:contains("Other Services")').text().lower()
        data['parties'] = 'parties' in pq('td:contains("Other Services")').text().lower()
        data['photography'] = 'photo' in pq('td:contains("Other Services")').text().lower()
        data['strippers'] = 'stripper' in pq('td:contains("Other Services")').text().lower()
        return data

    '''Extracts profile data fields from pyquery object-pq and stores in data object - item '''
    def extract_profile(self, pq, item):
        '''pq: PyQuery Object with data to extract'''
        '''item: item object that holds data'''

        phone = pq('b[itemprop="telephone"]').text()
        try:
            item['phone'] = self.get_phone(phone=phone)
        except:
            pass

        item['profile']['phone'] = self.anonymize_phone(phone)

        item['profileid'] = item['profile']['userid']
        item['profile']['name'] = pq('span[itemprop="name"]').text()
        item['profile']['availability'] = self.get_availability(pq)
        item['profile']['descriptions'] = pq('td.unSelectable').text()
        item['profile']['otherDescriptions'] = '. '.join([i.text() for i in pq('div[id*="content"]').items()]).replace('\n', '').lower()
        item['profile']['memberSince'] = pq('td.Label:contains("Member Since")').next().text()
        item['profile']['lastLogin'] = pq('td.Label:contains("Last Login")').next().text()
        item['profile']['views'] = pq('td.Label:contains("Views")').next().text()
        item['profile']['verified'] = pq('img[src="images/VerifiedLogo.gif"]') is not None
        item['profile']['hasMovies'] = pq('a.HomePageTabLink:contains("Movies")') is not None
        item['profile']['isToLet'] = 'to let' in pq('td:contains("Other Services")').text().lower()
        item['profile']['accessingFrom'] = pq('td.Label:contains("Accessing From")').next().text()
        item['profile']['hasPolls'] = self.get_user_polls(pq)

        imgbase = 'https://www.adultwork.com/dlgViewImage.asp?Image={}'
        item['profile']['image_links'] = [imgbase.format(i.attr('src')).replace('/t/', '/i/') for i in  pq('a[href*="switchImage"] img').items()] or []
        th = pq('a[onmouseover*="twitter.com"]')
        item['profile']['twitterHandle'] = th.attr('onmouseover').split('=')[-1].split(';')[0].replace("'", "") if th else ''

        ## Location Data
        item['profile']['location'] = self.get_location(pq)

        ## Demographic Data
        item['profile']['demographics'] = self.get_demographics(pq)

        ## Services Data
        item['profile']['services'] = self.get_services(pq)

        ## Preferences Data
        item['profile']['preferences'] = {}
        item['profile']['preferences']['with'] = pq('.PaddedLabel:contains("With:")').parent().parent().text().split('\n')
        item['profile']['preferences']['enjoys'] = pq('div#dPref table:contains("Enjoys")').text().split('\n')

        ## Pricing Data
        item['profile']['pricing'] = []

        # escort services prices
        durations = [i.text() for i in pq('td[id*="tdRT"]').items()]
        incallPrices = [i.text() for i in pq('td[id*="tdRI"]').items()]
        outcallPrices = [i.text() for i in pq('td[id*="tdRO"]').items()]
        for i in range(len(durations)):
            if len(incallPrices) != 0:
                item['profile']['pricing'].append({"serviceType":'incall', "price":incallPrices[i], "duration": durations[i]})
            if len(outcallPrices) != 0:
                item['profile']['pricing'].append({"serviceType":'outcall', "price":outcallPrices[i], "duration": durations[i]})

        # webcam data
        webcam_prices = pq('td.Padded:contains("To webcam via DirectCam")').next().next().text().split('per ')
        pc_prices = pq('td.Padded:contains("To phone chat via DirectCam")').next().next().text().split('per ')
        sms_prices = pq('td.Padded:contains("To book a phone chat session")').next().next().text().split('per ')
        if len(webcam_prices) > 1:
            item['profile']['pricing'].append({"serviceType":'webcam', "price":webcam_prices[0].split()[0], "duration":webcam_prices[-1].split()[0]})
        if len(pc_prices) > 1:
            item['profile']['pricing'].append({"serviceType":'webcam', "price":pc_prices[0].split()[0], "duration":pc_prices[-1].split()[0]})
        if len(sms_prices) > 1:
            item['profile']['pricing'].append({"serviceType":'webcam', "price":sms_prices[0].split()[0], "duration": sms_prices[-1].split()[0]})

         ## Tours Data
        item['tours'] = {}
        item['profile']['tourLink'] = 'https://www.adultwork.com/dlgUserTours.asp?UserID={}'.format(item['profile']['userid'])
        item['profile']['hasTours'] = 'Sorry, this member does not' not in requests.get(item['profile']['tourLink']).text

        ## Ratings Data
        item['ratings'] = {}
        item['profile']['ratingsLink'] = 'https://www.adultwork.com/dlgViewRatings.asp?UserID={}'.format(item['profile']['userid'])
        ratsdesc = pq('a[onclick*="viewRating"]').attr('title')
        if ratsdesc:
            item['profile']['ratings_total'] = ratsdesc.split(' - ')[0].split()[0]
            rts = ratsdesc.split(' - ')[1].split(',')
            item['profile']['ratings_positive'] = rts[0].split()[0].strip()
            item['profile']['ratings_neutral'] = rts[1].split()[0].strip()
            item['profile']['ratings_negative'] = rts[2].split()[0].strip()
            item['profile']['ratings_disputes'] = rts[3].split()[0].strip()
        item['profile']['hasRatings'] = 'There is no Feedback for this Member' not in requests.get(item['profile']['ratingsLink']).text

        ## Reviews Data
        item['reviews'] = {}
        reviews = pq('a[href*="vFR"]')
        item['profile']['hasReviews'] = len(reviews) != 0
        if item['profile']['hasReviews']:
            review_base_link = 'https://www.adultwork.com/ViewFieldReport.asp?FRID={}'
            reviewLinks = [i.attr('href').split("(")[-1].replace(")", "") for i in pq('a[href*="vFR"]').items()]
            item['profile']['reviewLinks'] = [review_base_link.format(i) for i in reviewLinks]
        return item

    '''Extracts tours data fields from pyquery object-pq and stores in data object-item'''
    def extract_tours(self, pq, item):
        item['tours']['tours'] = []
        tourDetails = pq('td.Padded:contains("Details")').parent()
        for tourDetail in tourDetails.items():
            cells = tourDetail('td')
            data = {}
            data['id'] = item['profileid']
            data['tourLink'] = item['profile']['tourLink']
            data['tour_desc'] = PyQuery(cells[2]).text()
            sts = PyQuery(cells[5]).text()
            data['stops'] = 1 if '1 in' in sts else sts
            data['where'] = sts.split('1 in ')[-1] if '1 in' in sts else 'Unknown'
            data['coordinates'] = self.get_lat_long(data['where']+ ', United Kingdom')
            data['starts'] = PyQuery(cells[3]).text()
            data['ends'] = PyQuery(cells[4]).text()
            item['tours']['tours'].append(data)
        return item

    '''Extracts ratings data fields from pyquery object-pq and stores in data object-item'''
    def extract_ratings(self, pq, item):
        #pq: PyQuery Object with data to extract
        #item: item object that holds data
        item['ratings']['ratings'] = []
        service_ratings = pq('table[id*="tbl"]').not_("[id*='Line']")
        for service in service_ratings.items():
            cells = [i('td') for i in service('tr').items()][2::]
            indexes = [i for i in range(0, len(cells)) if len(cells[i]) == 0]
            for index in indexes:
                m_list = cells[index-2:index]
                flattened = [item for sublist in m_list for item in sublist]
                data = [PyQuery(i).text() for i in flattened]
                data = [i for i in data if 'field report' not in i.lower()]

                foruser = [PyQuery(i)('a[href*="UserID="]') for i in flattened]
                foruser = [i for i in foruser if len(i) != 0]
                ff = None
                if len(foruser) != 0:
                    ff = PyQuery(foruser[0]).attr('href').split('UserID=')[-1].replace("'", "")


                if len(data) == 6:
                    by = data[1].lower()
                    data = {"id": item['profileid'], "for": item['profileid'], "service": service.attr('id').replace('tbl', ''), "type": data[0].replace('\n', ''), "by": by, "byid": ff, "date": data[2], "role": data[3],"serviceType":data[4], "description": data[5]}
                    item['ratings']['ratings'].append(data)
        return item

    '''Extracts reviews data fields from pyquery object-pq and stores in data object-item'''
    def extract_reviews(self, item):
        conn = AdultworkProfileUpdate(item['userid']).connect_db()
        db = conn.Adultwork
        self.reviewIds =  [i['frid'] for i in db.reviews.find()]

        #pq: PyQuery Object with data to extract
        #item: item object that holds data
        if item['profile']['hasReviews']:
            for reviewLink in item['profile']['reviewLinks']:
                frid = reviewLink.split('=')[-1].strip('/')
                if frid in self.reviewIds:
                    pass

                print('Detected New Client Review {} for {}. Updating Reviews.....'.format(frid, item['userid']))
                data, pq = {}, PyQuery(requests.get(reviewLink).text)
                data['id'] = item['profileid']
                data['frid'] = frid
                data['reviewLink'] = reviewLink
                data['for'] = pq('td.Label:contains("Report On:")').next().text().split("\xa0")[0]
                data['by'] = pq('td.Label:contains("Report By:")').next().text().lower()
                data['meetDate'] = pq('td.Label:contains("Meet Date:")').next().text()
                data['meetLocation'] = pq('td.Label:contains("Meet Location:")').next().text()
                data['coordinates'] = self.get_lat_long(data['meetLocation']+ ', United Kingdom')
                data['type'] =pq('td.Label:contains("Type:")').next().text()
                data['duration'] = pq('td.Label:contains("Time Spent:")').next().text() or pq('td.Label:contains("Duration:")').next().text()
                data['price'] = pq('td.Label:contains("Fee:")').next().text()
                data['recommended'] = pq('td.Label:contains("recommend:")').next().text()
                data['visitAgain'] = pq('td.Label:contains("visit again:")').next().text()
                data['valueForMoney'] = pq('td.Label:contains("for money:")').next().text()
                ovr = pq('td.Label:contains("Overall Rating:")').next().text().split()
                data['overallRatings'] = ovr[0] if len(ovr) > 0 else None

                data['feedback'] = {}

                data['feedback']['venue'] = {}
                data['feedback']['venue']['description'] = pq('td.Label:contains("About the Venue")').parent().next().next().text()
                data['feedback']['venue']['score'] = pq('td.Label:contains("About the Venue")').next().text().split('Score: ')[-1]

                data['feedback']['meeting'] = {}
                data['feedback']['meeting']['description'] = pq('td.Label:contains("About the Meeting")').parent().next().next().text()
                data['feedback']['meeting']['score'] = pq('td.Label:contains("About the Meeting")').next().text().split("Score: ")[-1]

                data['feedback']['worker'] = {}
                data['feedback']['worker']['attributes'] = {}

                data['feedback']['worker']['attributes']['physical'] = {}
                data['feedback']['worker']['attributes']['physical']['description'] = pq('i:contains("Physical")').parent().parent().next().text()
                data['feedback']['worker']['attributes']['physical']['score'] = pq('i:contains("Physical")').parent().next().text().split("Score: ")[-1]

                data['feedback']['worker']['attributes']['personality'] = {}
                data['feedback']['worker']['attributes']['personality']['description'] = pq('i:contains("Personality")').parent().parent().next().text()
                data['feedback']['worker']['attributes']['personality']['score'] = pq('i:contains("Personality")').parent().next().text().split("Score: ")[-1]

                data['feedback']['worker']['attributes']['service'] = {}
                data['feedback']['worker']['attributes']['service']['description'] = pq('i:contains("Service")').parent().parent().next().text()
                data['feedback']['worker']['attributes']['service']['score'] = pq('i:contains("Service")').parent().next().text().split("Score: ")[-1]
                item['reviews']['reviews'].append(data)
                sleep(1)
        return item
