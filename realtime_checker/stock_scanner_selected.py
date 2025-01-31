import helper
import drawCandle
import sys, os
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from datetime import datetime, timedelta
import candleStickScanner
import dataDownload
import threading
import time

symbols = helper.get_selected_symbol_list()
history_length = 50
date1 = (datetime.now() - timedelta(days=history_length, hours=0)).timetuple()[:3]
date2 = datetime.now().timetuple()[:3]

while True:
	for s in symbols:
		try:
			quotes = helper.get_data_from_file(s)
			stock_opening, stock_high, stock_low, stock_closing, stock_vol = helper.get_today_total(symbol=s)
			quote_with_date = ((quotes[-1][0] + 1), stock_opening, stock_high, stock_low, stock_closing, stock_vol)
			if datetime.now().weekday() == 0:
				#is monday
				quote_with_date = ((quotes[-1][0] + 3), stock_opening, stock_high, stock_low, stock_closing, stock_vol)
			print str(quote_with_date)
			quotes.append(quote_with_date)


		except Exception as e:
			print e
			continue

		stock_opening = [quotes[i][1] for i in xrange(len(quotes))]
		stock_high = [quotes[i][2] for i in xrange(len(quotes))]
		stock_low = [quotes[i][3] for i in xrange(len(quotes))]
		stock_closing = [quotes[i][4] for i in xrange(len(quotes))]
		stock_vol = [quotes[i][5] for i in xrange(len(quotes))]

		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive(stock_opening, stock_closing, lhv_arr)

		if lhv_con_arr[-1] == 1:
			drawCandle.draw_candle_stick_with_today(s, date1, date2, quotes, additional_function=drawCandle.show_result, data=lhv_con_index, name="L")

		time.sleep(5)
