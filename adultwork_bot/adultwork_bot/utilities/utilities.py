from datetime import date



class AAdultWorkUtilities(object):
    def __init__(self):
        self.description = 'This specifies the search parameters for form data to send with wirh post request'

    def get_today(self):
        ### get today's date to specify search timeframe with param 'hdteToday'
        today = datetime.date.today()
        return today_date = "{}/{}/{}".format(t.day, today.month, today.year)

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
        