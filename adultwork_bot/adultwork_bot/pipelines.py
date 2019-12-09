# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class AdultworkBotCleanerPipeline(object):
    def process_item(self, item, spider):
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
      
      if item['reviews']['hasReviews']:
         for review in item['reviews']['reviews']:
            self.db['reviews'].insert_one(review)

      if item['ratings']['hasRatings']:
         for rating in item['ratings']['ratings']:
            self.db['ratings'].insert_one(rating)

      if item['tours']['hasTours']:
         for tour in item['tours']['tours']:
            self.db['tours'].insert_one(tour)
      return item

class AdultworkBotSQLPipeline(object):
    def process_item(self, item, spider):
        return item

