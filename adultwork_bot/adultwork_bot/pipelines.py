# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo, datetime


class AdultworkBotCleanerPipeline(object):
   def cleanText(self, text):
      text = [i.strip().lower() for i in text.split('\n') if i != '']
      text = '. '.join(text)
      return text

   def process_last_login(self, lastlogin):
        if lastlogin == 'Today':
           lastlogin = datetime.datetime.now()
        elif lastlogin == 'Yesterday':
           lastlogin = datetime.datetime.now() - datetime.timedelta(1)
        else:
           lastlogin = lastlogin
        return lastlogin

   def process_reviewsList(self, reviewsList):
        for index in range(len(reviewsList)):
           if reviewsList[index]['duration'] != '':
              reviewsList[index]['duration'] = reviewsList[index]['duration'].split()[0]
           if reviewsList[index]['price'] != '':
              reviewsList[index]['price'] = ''.join([i for i in reviewsList[index]['price'] if i.isdigit() or i == '.'])
           if reviewsList[index]['feedback']['venue']['description'] != '':
              reviewsList[index]['feedback']['venue']['description'] = self.cleanText(reviewsList[index]['feedback']['venue']['description'])
              reviewsList[index]['feedback']['venue']['score'] = reviewsList[index]['feedback']['venue']['score'].split('/')[0].strip()
           if reviewsList[index]['feedback']['meeting']['description'] != '':
              reviewsList[index]['feedback']['meeting']['description'] = self.cleanText(reviewsList[index]['feedback']['meeting']['description'])
              reviewsList[index]['feedback']['meeting']['score'] = reviewsList[index]['feedback']['meeting']['score'].split('/')[0].strip()
           if reviewsList[index]['feedback']['worker']['attributes']['physical']['description'] != '':
              reviewsList[index]['feedback']['worker']['attributes']['physical']['description'] = self.cleanText(reviewsList[index]['feedback']['worker']['attributes']['physical']['description'])
              reviewsList[index]['feedback']['worker']['attributes']['physical']['score'] = reviewsList[index]['feedback']['worker']['attributes']['physical']['score'].split('/')[0].strip()
           if reviewsList[index]['feedback']['worker']['attributes']['personality']['description'] != '':
              reviewsList[index]['feedback']['worker']['attributes']['personality']['description'] = self.cleanText(reviewsList[index]['feedback']['worker']['attributes']['personality']['description'])
              reviewsList[index]['feedback']['worker']['attributes']['personality']['score'] = reviewsList[index]['feedback']['worker']['attributes']['personality']['score'].split('/')[0].strip()
           if reviewsList[index]['feedback']['worker']['attributes']['service']['description'] != '':
              reviewsList[index]['feedback']['worker']['attributes']['service']['description'] = self.cleanText(reviewsList[index]['feedback']['worker']['attributes']['service']['description'])
              reviewsList[index]['feedback']['worker']['attributes']['service']['score'] = reviewsList[index]['feedback']['worker']['attributes']['service']['score'].split('/')[0].strip()
        return reviewsList

   def process_item(self, item, spider):

      ## clean text descriptions
      item['profile']['descriptions'] = self.cleanText(item['profile']['descriptions'])
      item['profile']['otherDescriptions'] = self.cleanText(item['profile']['otherDescriptions'])


      if item['profile']['lastLogin'] != '':
          item['profile']['lastLogin'] = self.process_last_login(item['profile']['lastLogin'])

      if item['profile']['hasRatings']:
         for index in range(len(item['ratings']['ratings'])):
            item['ratings']['ratings'][index]['description'] = self.cleanText(item['ratings']['ratings'][index]['description'])

      ## clean reviews
      if item['profile']['hasReviews']:
          item['reviews']['reviews'] = self.process_reviewsList(item['reviews']['reviews'])
      return item



class AdultworkMongoPipeline(object):
   def __init__(self, mongo_db):
      self.mongo_db = mongo_db

   @classmethod
   def from_crawler(cls, crawler):
      return cls(
         mongo_db = crawler.settings.get('MONGO_DB', 'lists')
      )

   def connect_db(self):

      self.client = pymongo.MongoClient(host='localhost',port=27017)
      self.db = self.client[self.mongo_db]

   def process_item(self, item, spider):
      self.connect_db()

      self.db.profiles.insert(item['profile'])

      if item['profile']['lastLogin']:
          self.db.logins.insert({'userid': item['userid'], 'loggedin': item['profile']['lastLogin']})

      if 'phone' in item.keys():
          if self.db.phones.find_one({'stemmed': item['phone']['stemmed']}):
              self.db.phones.update({'stemmed': item['phone']['stemmed']}, {'$inc': {'linked_profiles': 1}})
          else:
              self.db.phones.insert(item['phone'])

      if item['profile']['hasTours']:
         for tour in item['tours']['tours']:
            self.db.tours.insert(tour)


      if item['profile']['hasReviews']:
         for review in item['reviews']['reviews']:
            self.db.reviews.insert(review)

      if item['profile']['hasRatings']:
         for rating in item['ratings']['ratings']:
            self.db.ratings.insert(rating)

      #return item
class AdultworkBotSQLPipeline(object):
    def process_item(self, item, spider):
        return item
