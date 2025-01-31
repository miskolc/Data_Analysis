import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc

import sys
import candleStickScanner
import resultTester
import helper
import drawCandle


symbols = helper.get_local_symbol_list()

net_gain_total = []

for s in symbols:
	try:
		quotes = helper.get_data_from_file(s, latest = 500)
	except Exception as e:
		print e
		continue

	if len(quotes) < 50:
		continue

	stock_opening = [quotes[i][1] for i in xrange(len(quotes))]
	stock_high = [quotes[i][2] for i in xrange(len(quotes))]
	stock_low = [quotes[i][3] for i in xrange(len(quotes))]
	stock_closing = [quotes[i][4] for i in xrange(len(quotes))]
	stock_vol = [quotes[i][5] for i in xrange(len(quotes))]

	def bulllish_hammer_test_gain1(net_gain_total):
		hammer_arr, hammer_index = candleStickScanner.scan_hammer(stock_opening, stock_closing, stock_high, stock_low)
		bullish_hammer_arr, bullish_hammer_index = candleStickScanner.scan_bullish_hammer(stock_opening, stock_closing, stock_high, stock_low, hammer_arr)
		if len(bullish_hammer_index) != 0:

			net_gain = resultTester.test_gain_1(stock_opening, stock_closing, bullish_hammer_index)
			net_gain_total += net_gain

	def lhvd_test_gain4(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		doji_arr, doji_index = candleStickScanner.scan_doji(stock_opening, stock_closing, stock_high, stock_low)
		range_arr, range_index = candleStickScanner.scan_high_moving_range(stock_opening, stock_closing)

		trade_arr = []
		trade_index = []

		for index in xrange(1, len(lhv_arr)):
			if lhv_arr[index - 1] == 1 and lhv_arr[index] == 1 and doji_arr[index] == 1 and range_arr[index - 1] == 1:
				trade_arr.append(1)
				trade_index.append(index)
			else:
				trade_arr.append(0)

		if len(trade_index) != 0:
			net_gain = resultTester.test_gain_4(stock_opening, stock_closing, trade_index)
			net_gain_total += net_gain

	def lhv_three_test_gain1(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive_three(stock_opening, stock_closing, lhv_arr)

		if len(lhv_con_index) != 0:
			net_gain = resultTester.test_gain_1(stock_opening, stock_closing, lhv_con_index)
			net_gain_total += net_gain

	def lhv_test_gain1(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive(stock_opening, stock_closing, lhv_arr, separate_by_price_moving_range=True)

		if len(lhv_con_index) != 0:
			net_gain = resultTester.test_gain_1(stock_opening, stock_closing, lhv_con_index)
			net_gain_total += net_gain

	def lhv_test_gain2(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive(lhv_arr)

		if len(lhv_con_index) != 0:
			net_gain = resultTester.test_gain_2(stock_opening, stock_closing, stock_high, lhv_con_index)
			net_gain_total += net_gain

	def lhv_test_gain3(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive(lhv_arr)

		if len(lhv_con_index) != 0:
			net_gain = resultTester.test_gain_3(stock_opening, stock_closing, lhv_con_index)
			net_gain_total += net_gain

	def lhv_test_gain4(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive(stock_opening, stock_closing, lhv_arr, separate_by_price_moving_range = True)

		if len(lhv_con_index) != 0:
			net_gain = resultTester.test_gain_4(stock_opening, stock_closing, lhv_con_index)
			net_gain_total += net_gain

	def lhv_test_gain5(net_gain_total):
		lhv_arr, lhv_index = candleStickScanner.scan_low_with_huge_vol(stock_opening, stock_closing, stock_high, stock_low, stock_vol)
		lhv_con_arr, lhv_con_index = candleStickScanner.scan_low_with_huge_vol_consecutive(stock_opening, stock_closing, lhv_arr, separate_by_price_moving_range = True)

		if len(lhv_con_index) != 0:
			net_gain = resultTester.test_gain_5(stock_opening, stock_closing, lhv_con_index)
			net_gain_total += net_gain


	def overall_test_gain1(net_gain_total):
		index_arr = [index for index in xrange(2, len(stock_opening) - 1)]
		net_gain = resultTester.test_gain_1(stock_opening, stock_closing, index_arr)
		net_gain_total += net_gain

	def overall_test_gain4(net_gain_total):
		index_arr = [index for index in xrange(2, len(stock_opening) - 1)]
		net_gain = resultTester.test_gain_4(stock_opening, stock_closing, index_arr)
		net_gain_total += net_gain

	lhv_test_gain5(net_gain_total)
	print ('Testing ', s, sum(net_gain_total))


print sum(net_gain_total) / len(net_gain_total)

print len(net_gain_total)

bin_list = []
for x in xrange(-100,100):
	bin_list.append(float(x)/100.0)
print bin_list

plt.hist(net_gain_total,bins=tuple(bin_list))
plt.yscale('log', nonposy='clip')
plt.show()