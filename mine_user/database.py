#!/usr/bin/env python
import pymongo
import datetime
from pymongo import MongoClient

class Database:
    def __init__(self):
        try:
            client = MongoClient('158.69.216.57', 27017)
            print "Connected successfully!!!"
        except pymongo.errors.ConnectionFailure, e:
           print "Could not connect to MongoDB: %s" % e
        self.db = client['extract']
        self.data = self.db['units']

# add a pin without detail info
    def add_unit_info(self, info):
        # print info
        if self.data.find_one({"_id": info["symbol"]}) == None:
            self.data.update({"_id": info["symbol"]}, info, upsert=True)
            print "add" + info["symbol"]

    def load_data(self):
        for entry in self.data.find():
            self.arr.append(int(entry["_id"][2:]))

    def get_greatest_amoung(self, start, end):
        lastGreatest = start
        for entry in self.arr:
            if entry > lastGreatest and entry < end:
                lastGreatest = entry
        return lastGreatest

    def print_amoung(self, start, end):
        lastGreatest = start
        for entry in self.arr:
            if entry > start and entry < end:
                print entry
