from requests import get


class TorController(object):
    def __init__(self):
        self.threshold = 5 ## maximum number of requests to use a single IP for before change is initiated
        self.attempts_for_new_ip = 10 ## maximum number of attempts to get a new IP address before giving up
        self.ip_init_wait = 0.5 ## wait for new ip to be initialized
        self.local_http_proxy = "127.0.0.1:8118"
        self.torhost = "127.0.0.1"
        self.torpassword = ""
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
        response = get(ican, proxies={"http": self.local_http_proxy})
        if response.status_code == 200:
            return response.text.strip()
        raise TorError("Failed to Obtain TOR IP Address")

    '''Change Current TOR Circuit'''
    def get_new_circuit(self):
        with Controller.from_port(address=self.toraddress, port=self.torport) as controller:
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
                raise TorError("Failed tor obtain new ip address")
            try:
                current_ip = self.get_current_tor_ip()
            except Exception as e:
                self.get_new_circuit()
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
            if len(self.used_ips) > self.threshold:
                del self.used_ips[0]

