# This class handle the extraction of data from pyquery objects for each data item
import string
import phonenumbers
import requests

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
        item['name'] = pq('span[itemprop="name"]').text()
        item['descriptions'] = pq('td.unSelectable').text()
        item['memberSince'] = pq('td.Label:contains("Member Since")').next().text()
        item['views'] = pq('td.Label:contains("Views")').next().text()
        item['verified'] = pq('img[src="images/VerifiedLogo.gif"]') is not None
        item['hasMovies'] = pq('a.HomePageTabLink:contains("Movies")') is not None
        item['isToLet'] = 'to let' in pq('td:contains("Other Services")').text().lower()
        item['accessingFrom'] = pq('td.Label:contains("Accessing From")').next().text()
        item['twitterHandle'] = pq('a[onmouseover*="twitter.com"]').attr('onmouseover').split('=')[-1].split(';')[0].replace("'", "")
        
        ## Location Data
        item['location'] = {}
        item['location']['town'] = pq('td.Label:contains("Town")').next().text()
        item['location']['county'] = pq('td.Label:contains("County")').next().text()
        item['location']['region'] = pq('td.Label:contains("Region")').next().text()
        item['location']['country'] = pq('td.Label:contains("Country")').next().text()

        ## Demographic Data
        item['demographics'] = {}
        item['demographics']['nationality'] = pq('td.Label:contains("Nationality")').next().text()
        item['demographics']['gender'] = pq('td.Label:contains("Gender")').next().text()
        item['demographics']['orientation'] = pq('td.Label:contains("Orientation")').next().text()
        item['demographics']['age'] = pq('td.Label:contains("Age")').next().text()
        item['demographics']['ethnicity'] = pq('td:contains("Ethnicity:")').next().text()
        item['demographics']['dressSize'] = pq('td:contains("Dress Size:")').next().text()
        item['demographics']['height'] = pq('td:contains("Height:")').next().text()
        item['demographics']['chestSize'] = pq('td:contains("Chest Size:")').next().text()
        item['demographics']['hairColor'] = pq('td:contains("Hair Colour:")').next().text()
        item['demographics']['eyeColor'] = pq('td:contains("Eye Colour:")').next().text()
        item['demographics']['phone'] = self.anonymize_phone(pq('b[itemprop="telephone"]').text())
        item['demographics']['phoneCarrier'] = self.get_carrier(pq('b[itemprop="telephone"]').text())

        ## Services Data
        item['services'] = {}
        item['services']['escort'] = 'escort' in pq('a[href*="javascript:makeBooking()"]').text().lower()
        item['services']['phoneChat'] = 'phone chat' in pq('a[href*="javascript:doPhoneChat()"]').text().lower()
        item['services']['smsChat'] = 'sms chat' in pq('a[href*="javascript:doSMSChat()"]').text().lower()
        item['services']['webcam'] = 'webcam' in pq('a[href*="javascript:dC"]').text().lower()
        item['services']['massage'] = 'massage' in pq('#main-content-container').text().lower().lower()
        item['services']['alternatives'] = [i for i in pq('span.ToolTip:contains("Alternative")').attr("title").replace('\r', '').split('\n')[1::] if i != '']
        item['services']['tolet'] = 'to let' in pq('td:contains("Other Services")').text().lower()
        item['services']['masseurs'] = 'masseur' in pq('td:contains("Other Services")').text().lower()
        item['services']['seekingModels'] = 'models wanted' in pq('td:contains("Other Services")').text().lower()
        item['services']['parties'] = 'parties' in pq('td:contains("Other Services")').text().lower()
        item['services']['photography'] = 'photo' in pq('td:contains("Other Services")').text().lower()
        item['services']['strippers'] = 'stripper' in pq('td:contains("Other Services")').text().lower()

        ## Preferences Data
        item['preferences'] = {}
        item['preferences']['with'] = ''
        item['preferences']['enjoys'] = pq('div#dPref table:contains("Enjoys")').text().split('\n')

        ## Pricing Data
        item['pricing'] = []

        # escort services prices
        durations = [i.text() for i in pq('td[id*="tdRT"]').items()]
        incallPrices = [i.text() for i in pq('td[id*="tdRI"]').items()]
        outcallPrices = [i.text() for i in pq('td[id*="tdRO"]').items()]
        for i in range(len(durations)):
            if len(incallPrices) != 0:
                item['pricing'].append({"serviceType":'incall', "price":incallPrices[i], "duration": durations[i]})
            if len(outcallPrices) != 0:
                item['pricing'].append({"serviceType":'outcall', "price":outcallPrices[i], "duration": durations[i]})

        # webcam data
        webcam_prices = pq('td.Padded:contains("To webcam via DirectCam")').next().next().text().split('per ')
        pc_prices = pq('td.Padded:contains("To phone chat via DirectCam")').next().next().text().split('per ')
        sms_prices = pq('td.Padded:contains("To book a phone chat session")').next().next().text().split('per ')
        if len(webcam_prices) > 1:
            item['pricing'].append({"serviceType":'webcam', "price":webcam_prices[0].split()[0], "duration":webcam_prices[-1].split()[0]})
        if len(pc_prices) > 1:
            item['pricing'].append({"serviceType":'webcam', "price":pc_prices[0].split()[0], "duration":pc_prices[-1].split()[0]})
        if len(sms_prices) > 1:
            item['pricing'].append({"serviceType":'webcam', "price":sms_prices[0].split()[0], "duration": sms_prices[-1].split()[0]})
        
       ## Reviews Data
       item['reviews'] = {}
       reviews = pq('a[href*="vFR"]')
       item['reviews']['hasReviews'] = len(reviews) != 0
       if item['reviews']['hasReviews']:
           item['reviews']['reviews'] = []
           reviewID = i.attr('href').split('vFR(')[-1].replace(')', '')
           reviewLink = 'https://www.adultwork.com/ViewFieldReport.asp?FRID={}'.format(reviewID)
           item['reviews']['reviews'] = [{"date":i.text(), "reviewID":reviewID, "reviewLink":reviewLink}]

        ## Ratings Data
        item['ratings'] = {}
        ratings_text = [i.strip().split()[0] for i in pq('a[onclick*="viewRating"]').attr('title').split('-')]
        item['ratings']['hasRatings'] = ratings_text[0].split()[0] != '0'
        if item['ratings']['hasRatings']:
            item['ratings']['ratingsLink'] = 'https://www.adultwork.com/dlgViewRatings.asp?UserID={}'.format(item['userid'])
            item['ratings']['total'] = ratings_text[0].split()[0]
            item['ratings']['positive'] = ratings_text[1].split()[0]
            item['ratings']['neutral'] = ratings_text[1].split()[2]
            item['ratings']['negative'] = ratings_text[1].split()[4]
            item['ratings']['disputes'] = ratings_text[1].split()[6]

        ## Tours Data
        item['tours'] = {}
        item['tours']['tourLink'] = 'https://www.adultwork.com/dlgUserTours.asp?UserID={}'.format(item['userid'])
        item['tours']['hasTours'] = 'Sorry, this member does not have any tours' not in requests.get(item['tours']['tourLink']).text
        return item 
    
    '''Extracts ratings data fields from pyquery object-pq and stores in data object - item '''
    def extract_ratings(self, pq, item):
        '''pq: PyQuery Object with data to extract'''
        '''item: item object that holds data'''
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
                if len(data) == 6:
                    data = {"for": item['userid'], "service": service.attr('id'), "type": data[0], "by": data[1], "date": data[2], "role": data[3],"serviceType":data[4], "description": data[5]}
                    item['ratings']['ratings'].append(data)
        return item


