# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime


class AdultworkBotCleanerPipeline(object):
   def cleanText(self, text):
      text = [i.strip().lower() for i in text.split('\n') if i != '']
      text = '. '.join(text)
      return text

   def process_item(self, item, spider):
            ## clean text descriptions
      item['profile']['descriptions'] = self.cleanText(item['profile']['descriptions'])
      item['profile']['otherDescriptions'] = self.cleanText(item['profile']['otherDescriptions'])
      
      #parse date time variables
      if item['profile']['memberSince'] != '':
         item['profile']['memberSince'] = datetime.datetime.strptime(item['profile']['memberSince'],'%d/%m/%Y')

      if item['profile']['lastLogin'] != '':
         if item['profile']['lastLogin'] == 'Today':
            item['profile']['lastLogin'] = datetime.datetime.now()
         elif item['profile']['lastLogin'] == 'Yesterday':
            item['profile']['lastLogin'] = datetime.datetime.now() - datetime.timedelta(1)
         else:
            item['profile']['lastLogin'] = datetime.datetime.strptime(item['profile']['lastLogin'],'%d/%m/%Y')
      
      if item['profile']['hasRatings']:
         for index in range(len(item['ratings']['ratings'])):
            if item['ratings']['ratings'][index]['date'] != '':
               item['ratings']['ratings'][index]['date'] = datetime.datetime.strptime(item['ratings']['ratings'][index]['date'], '%d/%m/%Y %H:%M')
               item['ratings']['ratings'][index]['description'] = self.cleanText(item['ratings']['ratings'][index]['description'])

      ## clean reviews
      if item['profile']['hasReviews']:
         for index in range(len(item['reviews']['reviews'])):
            if item['reviews']['reviews'][index]['meetDate'] != '':
               item['reviews']['reviews'][index]['meetDate'] = datetime.datetime.strptime(item['reviews']['reviews'][index]['meetDate'], '%A %d %B')
            if item['reviews']['reviews'][index]['duration'] != '':
               item['reviews']['reviews'][index]['duration'] = item['reviews']['reviews'][index]['duration'].split()[0]
            if item['reviews']['reviews'][index]['price'] != '':
               item['reviews']['reviews'][index]['price'] = ''.join([i for i in item['reviews']['reviews'][index]['price'] if i.isdigit() or i == '.'])
            if item['reviews']['reviews'][index]['feedback']['venue']['description'] != '':
               item['reviews']['reviews'][index]['feedback']['venue']['description'] = self.cleanText(item['reviews']['reviews'][index]['feedback']['venue']['description'])
               item['reviews']['reviews'][index]['feedback']['venue']['score'] = item['reviews']['reviews'][index]['feedback']['venue']['score'].split('/')[0].strip()
            if item['reviews']['reviews'][index]['feedback']['meeting']['description'] != '':
               item['reviews']['reviews'][index]['feedback']['meeting']['description'] = self.cleanText(item['reviews']['reviews'][index]['feedback']['meeting']['description'])
               item['reviews']['reviews'][index]['feedback']['meeting']['score'] = item['reviews']['reviews'][index]['feedback']['meeting']['score'].split('/')[0].strip()
            if item['reviews']['reviews'][index]['feedback']['worker']['attributes']['physical']['description'] != '':
               item['reviews']['reviews'][index]['feedback']['worker']['attributes']['physical']['description'] = self.cleanText(item['reviews']['reviews'][index]['feedback']['worker']['attributes']['physical']['description'])
               item['reviews']['reviews'][index]['feedback']['worker']['attributes']['physical']['score'] = item['reviews']['reviews'][index]['feedback']['worker']['attributes']['physical']['score'].split('/')[0].strip()
            if item['reviews']['reviews'][index]['feedback']['worker']['attributes']['personality']['description'] != '':
               item['reviews']['reviews'][index]['feedback']['worker']['attributes']['personality']['description'] = self.cleanText(item['reviews']['reviews'][index]['feedback']['worker']['attributes']['personality']['description'])
               item['reviews']['reviews'][index]['feedback']['worker']['attributes']['personality']['score'] = item['reviews']['reviews'][index]['feedback']['worker']['attributes']['personality']['score'].split('/')[0].strip()
            if item['reviews']['reviews'][index]['feedback']['worker']['attributes']['service']['description'] != '':
               item['reviews']['reviews'][index]['feedback']['worker']['attributes']['service']['description'] = self.cleanText(item['reviews']['reviews'][index]['feedback']['worker']['attributes']['service']['description'])
               item['reviews']['reviews'][index]['feedback']['worker']['attributes']['service']['score'] = item['reviews']['reviews'][index]['feedback']['worker']['attributes']['service']['score'].split('/')[0].strip()
       
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

      self.db['profiles'].insert(item['profile'])
      
      if item['profile']['hasReviews']:
         for review in item['reviews']['reviews']:
            self.db['reviews'].insert(review)

      if item['profile']['hasRatings']:
         for rating in item['ratings']['ratings']:
            self.db['ratings'].insert(rating)

      if item['profile']['hasTours']:
         for tour in item['tours']['tours']:
            self.db['tours'].insert(tour)
      #return item

class AdultworkBotSQLPipeline(object):
    def process_item(self, item, spider):
        return item

