from pymongo import MongoClient
from adultwork_bot.utilities.engine import AdultWorkEngine

'''This class is a profile updater for adult work, will update profiles for workers already captured'''
class AdultworkProfileUpdate(object):
    def __init__(self , userid):
        self.description = 'This class handles the update of fields Logins, date:location'
        self.userid = userid
        self.db = amp('Adultwork').connect_db()

    def update_location(self, pq):
        db_obj = self.db.profiles.find_one({'userid': self.userid})
        currentLocation = AdultWorkEngine().get_location(pq)
        previousLocation = db_obj['location']

        if currentLocation == previousLocation:
            pass
        else:
            print('Detected Location Change For {}. Updating Location Tracker.....'.format(self.userid))
            phone = pq('b[itemprop="telephone"]').text()
            anonp = AdultWorkEngine().anonymize_phone(phone)

            if self.db.phones.find({'number': anonp}).count() == 0:
                ph = AdultWorkEngine().get_phone(phone)
                self.db.phones.insert(ph)
                self.db.profiles.update({'userid': self.userid}, {'$set': {'phone': ph}})

            self.db.trackers.insert({datetime.today().strftime('%Y-%m-%d') : currentLocation, 'userid': self.userid, 'phone': anonp})
            self.db.profiles.update({'userid': self.userid}, {'$set': {'location': currentLocation}})
        conn.close()

    def update_logins(self, pq):
        db_obj = self.db.profiles.find_one({'userid': self.userid})
        pll = db_obj['lastLogin']
        last_available = db_obj['availabilty']
        current_available = AdultWorkEngine().self.get_availability(pq)
        cll = acp().process_last_login(pq('td.Label:contains("Last Login:")').next().text())

        if cll != pll:
            print('Detected new login details for {}...'.format(self.userid))
            self.db.logins.insert({'userid': self.userid, 'loggedin': cll})
        conn.close()

    def update_tours(self, pq):
        return 0

    def update_reviews(self, pq):
        reviews = [i['frid'] for i in self.db.reviews.find()]
        userreviews = pq('')
        return 0

    def update_ratings(self, pq):
        return 0

    def update_availability(self, pq):
        return 0
