from requests import get
from stem import Signal
from stem.control import Controller
from time import sleep

class TorIPError(Exception):
    pass

class TorController(object):
    def __init__(self):
        self.threshold = 5 ## maximum number of requests to use a single IP for before change is initiated
        self.attempts_for_new_ip = 10 ## maximum number of attempts to get a new IP address before giving up
        self.ip_init_wait = 0.5 ## wait for new ip to be initialized
        self.local_http_proxy = "127.0.0.1:8118"
        self.torhost = "127.0.0.1"
        self.torpassword = "aVe7ySt3althB0t"
        self.torport = 9051
        self.ican = "http://icanhazip.com/"
        self.unusable_ips = []

    '''This sets the real IP address of crawler host'''
    @property
    def my_ip(self):
        response = get(self.ican).text.strip()
        self.real_ip = response 
        return self.real_ip 
    
    '''This returns the current tor ip address'''
    def get_current_tor_ip(self):
        response = get(self.ican, proxies={"http": self.local_http_proxy})
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise TorIPError("Failed tor obtain new ip address")

    '''Change Current TOR Circuit'''
    def get_new_circuit(self):
        with Controller.from_port(address=self.torhost, port=self.torport) as controller:
            controller.authenticate(password=self.torpassword)
            controller.signal(Signal.NEWNYM)
        # Wait till the IP 'settles in'.
        sleep(self.ip_init_wait)

    '''Force Change TOR IP address'''
    def get_new_torip(self):
        #track the number of attempts
        attempts = 0
        while True:
            if attempts == self.threshold:
                raise TorIPError("Failed tor obtain new ip address")
            try:
                current_ip = self.get_current_tor_ip()
            except Exception as e:
                self.get_new_circuit()
                print(e)
                continue

            if current_ip in self.unusable_ips or current_ip == self.my_ip():
                self.get_new_circuit()
                continue
            
            self.pool_ips(current_ip)
            break
        return current_ip
        
    '''Manage Unusable ip address list'''
    def pool_ips(self, current_ip):
        # Add current IP to unsable ip addresses.
        self.unusable_ips.append(current_ip)

        # Release the oldest registred IP.
        if self.threshold:
            if len(self.unusable_ips) > self.threshold:
                del self.unusable_ips[0]



{'cboCountryID': '158', 'cboRegionID': '0', 'cboCountyID': '0', 'strTown': '', 'cboNationalityID': '0', 'rdoNationalityInclude': '1', 'cboSCID': '0', 'cboAPID': '0', 'strKeywords': '', 'rdoKeySearch': '1', 'cboLastLoginSince': 'X', 'strSelUsername': '', 'intAgeFrom': '', 'intAgeTo': '', 'rdoOrderBy': '1', 'rdoRatings': '0', 'question_1': '(select)', 'question_69': '', 'question_70': '', 'question_84': '', 'question_2': '', 'question_3': '', 'question_4': '(select)', 'question_5': '(select)', 'question_57': '', 'question_7': '(select)', 'question_8': '(select)', 'question_9': '(select)', 'question_10': '(select)', 'question_82': '(select)', 'GC_11': '(select)', 'question_11': '(select)', 'GC_46': '(select)', 'question_46': '(select)', 'GC_47': '(select)', 'question_47': '(select)', 'GC_58': '(select)', 'question_58': '(select)', 'GC_12': '(select)', 'question_12': '(select)', 'question_13': '(select)', 'GC_80': '(select)', 'question_80': '(select)', 'question_81': '(select)', 'question_14': '(select)', 'question_67': '(select)', 'question_49': '(select)', 'question_27': '', 'question_42': '', 'dteMeetDate': '', 'dteMeetTime': 'X', 'intMeetDuration': '', 'intMeetPrice': '', 'cboBookingCurrencyID': '28', 'intHalfHourRateFrom': '', 'intHalfHourRateTo': '', 'intHourlyRateFrom': '', 'intHourlyRateTo': '', 'intOvernightRateFrom': '', 'intOvernightRateTo': '', 'dteAvailableAnotherDay': '', 'intMiles': '', 'strSelPostCode': '', 'strPostCodeArea': '', 'cboLastUpdated': '01/01/2003', 'intHotListID': '0', 'CommandID': '3', 'PageNo': '3', 'HotListSearch': '0', 'SearchTab': 'Profile', 'hdteToday': '04/12/2019', 'DF': '1', 'SS': '0'}