''' This handles the extraction of data from pyquery objects for each data item '''

import string
import phonenumbers
import requests
from pyquery import PyQuery
from time import sleep

class AdultWorkEngine(object):
    def __init__(self):
        self.description = 'This class handle the extraction of data from pyquery objects for each data item'

    def anonymize_phone(self, phone):
        letters = string.ascii_lowercase
        phone = ''.join([letters[int(i)] for i in phone.split('+')[-1]])
        return phone
    
    def get_carrier(self, phone):
        ro_num = phonenumbers.parse(phone, "RO")
        return phonenumbers.carrier.name_for_number(ro_num, "en")

    '''Extracts profile data fields from pyquery object-pq and stores in data object - item '''
    def extract_profile(self, pq, item):
        '''pq: PyQuery Object with data to extract'''
        '''item: item object that holds data'''
        item['profileid'] = item['profile']['userid']
        item['profile']['name'] = pq('span[itemprop="name"]').text()
        item['profile']['descriptions'] = pq('td.unSelectable').text()
        item['profile']['otherDescriptions'] = '. '.join([i.text() for i in pq('div[id*="content"]').items()]).replace('\n', '').lower()
        item['profile']['memberSince'] = pq('td.Label:contains("Member Since")').next().text()
        item['profile']['lastLogin'] = pq('td.Label:contains("Last Login")').next().text()
        item['profile']['views'] = pq('td.Label:contains("Views")').next().text()
        item['profile']['verified'] = pq('img[src="images/VerifiedLogo.gif"]') is not None
        item['profile']['hasMovies'] = pq('a.HomePageTabLink:contains("Movies")') is not None
        item['profile']['isToLet'] = 'to let' in pq('td:contains("Other Services")').text().lower()
        item['profile']['accessingFrom'] = pq('td.Label:contains("Accessing From")').next().text()
        imgbase = 'https://www.adultwork.com/dlgViewImage.asp?Image={}'
        item['profile']['image_links'] = [imgbase.format(i.attr('src')).replace('/t/', '/i/') for i in  pq('a[href*="switchImage"] img').items()] or None
        th = pq('a[onmouseover*="twitter.com"]')
        item['profile']['twitterHandle'] = th.attr('onmouseover').split('=')[-1].split(';')[0].replace("'", "") if th else ''
        
        ## Location Data
        item['profile']['location'] = {}
        item['profile']['location']['town'] = pq('td.Label:contains("Town")').next().text()
        item['profile']['location']['county'] = pq('td.Label:contains("County")').next().text()
        item['profile']['location']['region'] = pq('td.Label:contains("Region")').next().text()
        item['profile']['location']['country'] = pq('td.Label:contains("Country")').next().text()

        ## Demographic Data
        item['profile']['demographics'] = {}
        item['profile']['demographics']['nationality'] = pq('td.Label:contains("Nationality")').next().text()
        item['profile']['demographics']['gender'] = pq('td.Label:contains("Gender")').next().text()
        item['profile']['demographics']['orientation'] = pq('td.Label:contains("Orientation")').next().text()
        item['profile']['demographics']['age'] = pq('td.Label:contains("Age")').next().text()
        item['profile']['demographics']['ethnicity'] = pq('td:contains("Ethnicity:")').next().text()
        item['profile']['demographics']['dressSize'] = pq('td:contains("Dress Size:")').next().text()
        item['profile']['demographics']['height'] = pq('td:contains("Height:")').next().text()
        item['profile']['demographics']['chestSize'] = pq('td:contains("Chest Size:")').next().text()
        item['profile']['demographics']['hairColor'] = pq('td:contains("Hair Colour:")').next().text()
        item['profile']['demographics']['eyeColor'] = pq('td:contains("Eye Colour:")').next().text()
        item['profile']['demographics']['phone'] = self.anonymize_phone(pq('b[itemprop="telephone"]').text())
        #item['demographics']['phoneCarrier'] = self.get_carrier(pq('b[itemprop="telephone"]').text())

        ## Services Data
        item['profile']['services'] = {}
        item['profile']['services']['escort'] = 'escort' in pq('a[href*="javascript:makeBooking()"]').text().lower()
        item['profile']['services']['phoneChat'] = 'phone chat' in pq('a[href*="javascript:doPhoneChat()"]').text().lower()
        item['profile']['services']['smsChat'] = 'sms chat' in pq('a[href*="javascript:doSMSChat()"]').text().lower()
        item['profile']['services']['webcam'] = 'webcam' in pq('a[href*="javascript:dC"]').text().lower()
        item['profile']['services']['massage'] = 'massage' in pq('#main-content-container').text().lower().lower()
        ats = pq('span.ToolTip:contains("Alternative")').attr("title")
        item['profile']['services']['alternatives'] = [i for i in ats.replace('\r', '').split('\n')[1::] if i != ''] if ats else []
        item['profile']['services']['tolet'] = 'to let' in pq('td:contains("Other Services")').text().lower()
        item['profile']['services']['masseurs'] = 'masseur' in pq('td:contains("Other Services")').text().lower()
        item['profile']['services']['seekingModels'] = 'models wanted' in pq('td:contains("Other Services")').text().lower()
        item['profile']['services']['parties'] = 'parties' in pq('td:contains("Other Services")').text().lower()
        item['profile']['services']['photography'] = 'photo' in pq('td:contains("Other Services")').text().lower()
        item['profile']['services']['strippers'] = 'stripper' in pq('td:contains("Other Services")').text().lower()

        ## Preferences Data
        item['profile']['preferences'] = {}
        item['profile']['preferences']['with'] = ''
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

       

    #Extracts tours data fields from pyquery object-pq and stores in data object-item
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
            data['starts'] = PyQuery(cells[3]).text()
            data['ends'] = PyQuery(cells[4]).text()
            item['tours']['tours'].append(data)
        return item

    #Extracts ratings data fields from pyquery object-pq and stores in data object-item 
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
    
    #Extracts reviews data fields from pyquery object-pq and stores in data object-item
    def extract_review(self, item):
        #pq: PyQuery Object with data to extract
        #item: item object that holds data
        if item['profile']['hasReviews']:
            for reviewLink in item['profile']['reviewLinks']:
                data, pq = {}, PyQuery(requests.get(reviewLink).text)
                data['id'] = item['profileid']
                data['reviewLink'] = reviewLink
                data['for'] = pq('td.Label:contains("Report On:")').next().text().split("\xa0")[0]
                data['by'] = pq('td.Label:contains("Report By:")').next().text().lower()
                data['meetDate'] = pq('td.Label:contains("Meet Date:")').next().text()
                data['meetLocation'] = pq('td.Label:contains("Meet Location:")').next().text()
                data['type'] =pq('td.Label:contains("Type:")').next().text()
                data['duration'] = pq('td.Label:contains("Time Spent:")').next().text() or pq('td.Label:contains("Duration:")').next().text()
                data['price'] = pq('td.Label:contains("Fee:")').next().text()
                data['recommended'] = pq('td.Label:contains("recommend:")').next().text()
                data['visitAgain'] = pq('td.Label:contains("visit again:")').next().text()
                data['valueForMoney'] = pq('td.Label:contains("for money:")').next().text()
                data['overallRatings'] = pq('td.Label:contains("Overall Rating:")').next().text().split()[0] or None

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

    
        



        


