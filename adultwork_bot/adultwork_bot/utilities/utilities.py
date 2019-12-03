from bs4 import  BeautifulSoup
from random import choice, shuffle
from fake_useragent import UserAgent
from requests import get
import datetime



class AdultWorkSearchParameters(object):
    def __init__(self):
        self.description = 'This specifies the search parameters for form data to send with wirh post request'

    def get_today(self):
        ### get today's date to specify search timeframe with param 'hdteToday'
        today = datetime.date.today()
        return "{}/{}/{}".format(today.day, today.month, today.year)

    def uk_search_params(self):
        params = {"formdata":
            {
                "cboPageNo": "1", "cboCountryID":"158", "cboRegionID":"0", "cboCountyID":"0", "cboNationalityID":"0",
                "rdoNationalityInclude":"1", "cboSCID":"0", "cboAPID":"0", "rdoKeySearch":"1", "cboLastLoginSince":"X",
                "rdoOrderBy":"1", "rdoRatings":"0", "cboBookingCurrencyID":"28", "cboLastUpdated":"01/01/2003",
                "intHotListID":"0", "CommandID":"2", "PageNo":"1", "HotListSearch":"0", "SearchTab":"Profile",
                "hdteToday":self.get_today(), "DF":"1", "SS":"0"
                }
            }
        return params 

class Pooling(object):
    def __init__(self):
        self.description = 'Rotating Proxies and User Agents for Bot'
        self.proxiesurl = ["https://www.us-proxy.org/","https://free-proxy-list.net/uk-proxy.html"]
        self.ua = UserAgent(cache=False)

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
        self.ua.update()

        ##select chrome and firefox useragents
        browsers = self.ua.data['browsers']['chrome'] + self.ua.data['browsers']['firefox']
        shuffle(browsers)
        return choice(browsers)
