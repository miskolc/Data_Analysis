#!/usr/bin/env python
from DefaultVariables import *
import pymongo
from pymongo import *
from bson.objectid import ObjectId
import datetime, time
import Helper

class Database:
    def __init__(self):
        try:
            self.client = MongoClient('127.0.0.1', 27017)
            print "create db instance"
        except pymongo.errors.ConnectionFailure, e:
            print "Could not connect to MongoDB: %s" % e
        self.db = self.client[DATABASE_NAME]
        self.currency_list = self.db['currency_list']
        self.realtime_data = self.db["realtime_data"]
        self.trading_history = self.db["trading_history"]
        self.open_trades = self.db["open_trades"]
        self.mock_trading_history = self.db["mock_trading_history"]
        self.mock_open_trades = self.db["mock_open_trades"]
    def add_historical_trades(self, symbol, trade_price, trade_time, is_up, close_time, close_price, result):
        self.trading_history.insert({"symbol":symbol, "trade_price": float(trade_price), "trade_time": int(trade_time), "is_up": is_up, "close_time": int(close_time), "close_price": close_price, "result":result})

    def add_open_trades(self, symbol, trade_price, trade_time, is_up, close_time):
        self.open_trades.insert({"symbol":symbol, "trade_price": float(trade_price), "trade_time": int(trade_time), "is_up": is_up, "close_time": int(close_time)})

    def add_mock_historical_trades(self, symbol, trade_price, trade_time, is_up, close_time, close_price, result):
        self.mock_trading_history.insert({"symbol":symbol, "trade_price": float(trade_price), "trade_time": int(trade_time), "is_up": is_up, "close_time": int(close_time), "close_price": close_price, "result":result})

    def add_mock_open_trades(self, symbol, trade_price, trade_time, is_up, close_time):
        self.mock_open_trades.insert({"symbol":symbol, "trade_price": float(trade_price), "trade_time": int(trade_time), "is_up": is_up, "close_time": int(close_time)})

    def get_realtime_Data(self, symbol, length):
        result = []
        date = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y%m%d')
        data = self.realtime_data.find_one({"symbol": symbol, "date":str(date)})["data"]
        index = 0
        while len(result) < length:
            minute_in_unix = int(time.time()) / 60 * 60 - index * 60
            if date != datetime.datetime.fromtimestamp(minute_in_unix).strftime('%Y%m%d'):
                date = datetime.datetime.fromtimestamp(minute_in_unix).strftime('%Y%m%d')
                data = self.realtime_data.find_one({"symbol": symbol, "date":str(date)})["data"]
            if str(minute_in_unix) in data:
                result.insert(0, data[str(minute_in_unix)])
            index += 1

        if len(result) == length:
            return result
        return None

    def get_realtime_date_Data(self, symbol, date):
        result = []
        date_in_unix = int(time.mktime(datetime.datetime.strptime(str(date), "%Y%m%d").timetuple()))
        data = self.realtime_data.find_one({"symbol": symbol, "date":str(date)})["data"]
        
        for index in range(MINUTES_PER_DAY):
            minute_in_unix = date_in_unix + index * 60
            if str(minute_in_unix) in data:
                result.append(data[str(minute_in_unix)])
            else:
                print "missing minute"

        return result

    def get_currency_list(self):
        c_list = [currency for currency in self.currency_list.find()]
        return c_list

    def get_available_currency_list(self):
        collections = [collection for collection in self.db.collection_names() if self.currency_list.find({"symbol": collection}).count() == 1]
        return collections

    def get_one_day_currency_data(self, symbol, date):

        date = int(date)
        Helper.is_valid_symbol(symbol)
        Helper.is_valid_date(date)

        return self.db[symbol].find_one({"date": date})

    def get_range_currency_date(self, symbol, start, end):

        start = int(start)
        end = int(end)
        Helper.is_valid_symbol(symbol)
        Helper.is_valid_date(start)
        Helper.is_valid_date(end)
        start_time = int(time.mktime(datetime.datetime.strptime(str(start), "%Y%m%d").timetuple()))
        end_time = int(time.mktime(datetime.datetime.strptime(str(end), "%Y%m%d").timetuple()))
        results = []
        for day_date in self.db[symbol].find({'unix_time': {'$gte': start_time, '$lte': end_time}}):
            results.append(day_date)
        results = sorted(results, key=lambda k: k['unix_time'])
        return results

    def close(self):
        self.client.close()