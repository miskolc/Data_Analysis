#!/usr/bin/env python
import pymongo
from pymongo import *
from bson.objectid import ObjectId
import datetime

class Database:
    def __init__(self):
        try:
            client = MongoClient('127.0.0.1', 27017)
            print "Connected successfully!!!"
        except pymongo.errors.ConnectionFailure, e:
           print "Could not connect to MongoDB: %s" % e
        self.db = client['Stock_Database']
        self.symbol_list = self.db['symbol_list']

    def get_full_stock_dict(self):
        result_dict = {}
        for item in self.symbol_list.find():
            result_dict[item["symbol"]] = item["url"]
        return result_dict

    def get_alpha_stock_dict(self):
        result_dict = {}
        for item in self.symbol_list.find({"isalpha": True}):
            result_dict[item["symbol"]] = item["url"]
        return result_dict

    def upsert_stock_data(self, symbol, data):
        self.db[symbol].update({"date": data["date"]}, data, True)

    def update_stock_url(self, symbol, url):
        info = self.symbol_list.find_one({"symbol": symbol})
        info["url"] = url
        self.symbol_list.update({"_id": info["_id"]}, info, True)