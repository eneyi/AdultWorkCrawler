from bs4 import  BeautifulSoup
from random import choice, shuffle
#from fake_useragent import UserAgent
from requests import get
import datetime
from pymongo import MongoClient



class AdultWorkSearchParameters(object):
    def __init__(self):
        self.description = 'This specifies the search parameters for form data to send with wirh post request'

    def get_today(self):
        ### get today's date to specify search timeframe with param 'hdteToday'
        today = datetime.date.today()
        return "{}/{}/{}".format(today.day, today.month, today.year)

    def uk_search_params(self):
        params = {"formdata":{"cboCountryID":"158","cboRegionID":"0","cboCountyID":"0","strTown":"","cboNationalityID":"0","rdoNationalityInclude":"1","cboSCID":"0","cboAPID":"0","strKeywords":"","rdoKeySearch":"1","cboLastLoginSince":"X","strSelUsername":"","intAgeFrom":"","intAgeTo":"","rdoOrderBy":"1","rdoRatings":"0","question_1":"(select)","question_69":"","question_70":"","question_84":"","question_2":"","question_3":"","question_4":"(select)","question_5":"(select)","question_57":"","question_7":"(select)","question_8":"(select)","question_9":"(select)","question_10":"(select)","question_82":"(select)","GC_11":"(select)","question_11":"(select)","GC_46":"(select)","question_46":"(select)","GC_47":"(select)","question_47":"(select)","GC_58":"(select)","question_58":"(select)","GC_12":"(select)","question_12":"(select)","question_13":"(select)","GC_80":"(select)","question_80":"(select)","question_81":"(select)","question_14":"(select)","question_67":"(select)","question_49":"(select)","question_27":"","question_42":"","dteMeetDate":"","dteMeetTime":"X","intMeetDuration":"","intMeetPrice":"","cboBookingCurrencyID":"28","intHalfHourRateFrom":"","intHalfHourRateTo":"","intHourlyRateFrom":"","intHourlyRateTo":"","intOvernightRateFrom":"","intOvernightRateTo":"","dteAvailableAnotherDay":"","intMiles":"","strSelPostCode":"","strPostCodeArea":"","cboLastUpdated":"01/01/2003","intHotListID":"0","CommandID":"2","PageNo":"1","HotListSearch":"0","SearchTab":"Profile","hdteToday":"04/12/2019","DF":"1","SS":"0"}}
        return params 

class Pooling(object):
    def __init__(self):
        self.description = 'Rotating Proxies and User Agents for Bot'
        self.proxiesurl = ["https://free-proxy-list.net/"]
        #self.ua = UserAgent(cache=False)
        self.ua_url = 'https://raw.githubusercontent.com/cvandeplas/pystemon/master/user-agents.txt'

    '''Rotating Proxies'''
    def proxy_pool(self):
        ##define proxy web source, you can change this function if paid proxies available
        proxy_page = choice(self.proxiesurl)

        ## beautiful soup to get ips and ports
        soup = BeautifulSoup(get(proxy_page).content)
        proxy_rows = soup.find("table",{"id":"proxylisttable"}).find("tbody").findAll("tr")

        ##filter out transperent proxies
        proxies = [{"ip":i.findAll("td")[0].string,"port":i.findAll("td")[1].string} for i in proxy_rows if i.findAll("td")[4].string != "transparent"]
        proxies = ["http://"+i['ip']+":"+i['port'] for i in proxies]

        ###check that at least 2 proxies are returned before overwriting current proxy list
        if len(proxies) > 1:
            with open("proxies.txt", "w+") as ff:
                for proxy in proxies:
                    ff.write(proxy+"\n")
                ff.close()
        return proxies

    '''Rotating User Agent'''
    def ua_pool(self):
        #self.ua.update()

        #get browsers
        with open(self.ua_url, 'r+') as ff:
            browsers = [i.strip() for i in ff.readlines()]
        ff.close()

        ##select chrome and firefox useragents
        #browsers = self.ua.data['browsers']['chrome'] + self.ua.data['browsers']['firefox']
        shuffle(browsers)
        return choice(browsers)

class db(object):

    def __init__(self):
        self.description = 'Database functions'

    def connect_mongo(self, database):
        client = MongoClient(host='localhost',port=27017)
        db = client[database]
        return db 
