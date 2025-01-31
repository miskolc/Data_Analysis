from Crawler import Crawler
from DefaultVariables import *
from Database import Database
import Helper
from Line import Line
import threading
import zipfile
import time, os, sys, datetime
import matplotlib.pyplot as plt
import operator
import Plot
import numpy as np
import math
from SupportResistance import compute_support_resistance
from matplotlib.dates import date2num
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier

def parse_historical_data(serialized_chunk):

	good_result_threshold = 3

	chunk_results = []
	for chunk in serialized_chunk:
		close = []
		high = []
		low = []
		opening = []
		unix_time = []
		good_result = []
		for index in range(len(chunk)):
			if chunk[index]["tick_count"] == 0:
				if chunk[index + 1]["tick_count"] == 0 and chunk[index - 1]["tick_count"] == 0:
					print "consecutive missing minutes"
					# raise Exception("consecutive missing minutes")
				elif chunk[index + 1]["tick_count"] == 0:
					p_c_minute = int(chunk[index - 1]["seconds_data"][0]["unix_time"]) / 60 * 60
					prev_last = chunk[index - 1]["last"]
					opening.append(prev_last)
					close.append(prev_last)
					high.append(prev_last)
					low.append(prev_last)
					good_result.append(0.0)
					unix_time.append(p_c_minute + 60)

				elif chunk[index - 1]["tick_count"] == 0:
					next_first = chunk[index + 1]["first"]
					opening.append(next_first)
					close.append(next_first)
					high.append(next_first)
					low.append(next_first)
					n_c_minute = int(chunk[index + 1]["seconds_data"][0]["unix_time"]) / 60 * 60
					if int(chunk[index + 1]["seconds_data"][0]["unix_time"]) - n_c_minute <= good_result_threshold:
						good_result.append(chunk[index + 1]["seconds_data"][0]["price"])
					else:
						good_result.append(0.0)
					unix_time.append(n_c_minute - 60)
				else:					
					prev_last = chunk[index - 1]["last"]
					next_first = chunk[index + 1]["first"]
					opening.append(prev_last)
					close.append(next_first)
					high.append(max(prev_last,next_first))
					low.append(min(prev_last,next_first))
					n_c_minute = int(chunk[index + 1]["seconds_data"][0]["unix_time"]) / 60 * 60
					if int(chunk[index + 1]["seconds_data"][0]["unix_time"]) - n_c_minute <= good_result_threshold:
						good_result.append(chunk[index + 1]["seconds_data"][0]["price"])
					else:
						good_result.append(0.0)
					unix_time.append(n_c_minute - 60)

			else:
				c_minute = int(chunk[index]["seconds_data"][0]["unix_time"]) / 60 * 60
				if (c_minute + 60) - int(chunk[index]["seconds_data"][-1]["unix_time"]) <= good_result_threshold:
					good_result.append(chunk[index]["seconds_data"][-1]["price"])
				elif index + 1 < len(chunk) and chunk[index + 1]["tick_count"] > 0 and int(chunk[index + 1]["seconds_data"][0]["unix_time"]) - (c_minute + 60) <= good_result_threshold:
					good_result.append(chunk[index + 1]["seconds_data"][0]["price"])
				else:
					good_result.append(0.0)

				high.append(chunk[index]["high"])
				low.append(chunk[index]["low"])
				opening.append(chunk[index]["first"])
				close.append(chunk[index]["last"])
				unix_time.append(c_minute)
		chunk_results.append([unix_time, opening, high, low, close, good_result])

	return chunk_results

def choose_top_five_lines(resistance_lines, support_lines, frame_size):
	good_support = []
	for l in reversed(support_lines[-5:]):
		good_support.append(l["line"])

	good_resisitance = []

	resistance_end_points = []
	for l in reversed(resistance_lines[-5:]):
		good_resisitance.append(l["line"])

	return (good_support, good_resisitance)

def choose_best_line(resistance_lines, support_lines, frame_size):
	support_end_points = []
	good_support = []
	support_slope = []
	for l in reversed(support_lines[-7:]):
		good_support.append(l["line"])
		support_slope.append(l["line"].slope)
		support_end_points.append(l["line"].get_y(0))
		support_end_points.append(l["line"].get_y(frame_size))
	good_resisitance = []
	resistance_slope = []

	resistance_end_points = []
	for l in reversed(resistance_lines[-7:]):
		good_resisitance.append(l["line"])
		resistance_slope.append(l["line"].slope)
		resistance_end_points.append(l["line"].get_y(0))
		resistance_end_points.append(l["line"].get_y(frame_size))

	normalize_slope_val = max(resistance_end_points) - min(support_end_points) 
	resistance_slope.remove(max(resistance_slope))
	resistance_slope.remove(min(resistance_slope))
	support_slope.remove(max(support_slope))
	support_slope.remove(min(support_slope))

	good_lines = []
	for index in range(2):
		good_lines.append([good_support[index], good_resisitance[index]])

	final_support = Line(2,2,1,1)
	final_support.slope = (good_lines[0][0].slope+good_lines[1][0].slope)/2
	final_support.intercept = (good_lines[0][0].intercept+good_lines[1][0].intercept)/2

	final_resistance = Line(2,2,1,1)
	final_resistance.slope = (good_lines[0][1].slope+good_lines[1][1].slope)/2
	final_resistance.intercept = (good_lines[0][1].intercept+good_lines[1][1].intercept)/2
	return (final_support, final_resistance)

def get_ML_data_for_resistance_support(symbol = "EURUSD", start_time = 20151003, end_time = 20160213):
	db = Database()
	currency_data = db.get_range_currency_date(symbol, start_time ,end_time)
	suppose_unix_time = int(time.mktime(datetime.datetime.strptime(str(start_time), "%Y%m%d").timetuple()))
	serialized_chunk = [[]]

	for day_data in currency_data:
		print day_data["unix_time"]
		if day_data["unix_time"] != suppose_unix_time:
			serialized_chunk.append([])
			suppose_unix_time = day_data["unix_time"]
			print "  "

		serialized_chunk[-1] = serialized_chunk[-1] + day_data["minute_price"]
		suppose_unix_time += SECONDS_PER_DAY

	for chunk_index in range(len(serialized_chunk)):
		start_index = 0
		for minute_data in serialized_chunk[chunk_index]:
			if minute_data["tick_count"] == 0:
				start_index += 1
			else:
				break
		end_index = len(serialized_chunk[chunk_index])
		for minute_data in reversed(serialized_chunk[chunk_index]):
			if minute_data["tick_count"] == 0:
				end_index -= 1
			else:
				break
		serialized_chunk[chunk_index] = serialized_chunk[chunk_index][start_index: end_index]
		# print start_index
		# print end_index

	result = parse_historical_data(serialized_chunk)

	for chunk in result:
		for x in range(5):
			if len(chunk[5]) != len(chunk[x]):
				raise Exception("data length inconsistent")

	return result


def evaluate_output(output, testing_set_result):
	total_count = 0
	true_count = 0
	correct_count = 0
	for index in range(len(output)):
		# print (output[index], testing_set_result[index])
		if output[index] == testing_set_result[index]:
			correct_count += 1
		if output[index] == 1:
			total_count += 1 
			if testing_set_result[index] == 1:
				true_count += 1
		if output[index] == -1:
			total_count += 1 
			if testing_set_result[index] == -1:
				true_count += 1

	print (true_count, total_count) 
	print float(true_count) / float(total_count)
	print (correct_count, len(output))
	print float(correct_count) / float(len(output))
	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

training_data = []
training_result = []

training_data_path = os.path.join(os.getcwd(),"Training")
for file in os.listdir(training_data_path):
	print file
	if file[-3:] == "txt":
		with open(os.path.join(training_data_path, file), "r") as open_file:
		    for line in open_file:
		    	training_result.append(int(line.split("|")[1][:-1]))
		    	features_arr = []
		    	raw_features = line.split("|")[0][1:-1].split(",")
		    	for index in range(len(raw_features)):
		    		if index == 6 or index == 7 or index == 8:
		    			features_arr.append(float(raw_features[index]))
		    		else:
		    			features_arr.append(int(raw_features[index]))
		    	training_data.append(features_arr)


threshold = len(training_data)/3
training_set = training_data[:threshold]
training_set_result = training_result[:threshold]
testing_set = training_data[threshold:]
testing_set_result_all = training_result[threshold:]

def evaluate_proba_output(output, output_proba, testing_set_result, threshold):
	total_count = 0
	true_count = 0
	for index in range(len(output)):
		if output_proba[index][output[index] + 1] > threshold:
			total_count += 1 
			if testing_set_result[index] == output[index]:
				true_count += 1

	print (true_count, total_count) 
	print float(true_count) / float(total_count)
	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

forest = RandomForestClassifier(n_estimators = 100)
forest = forest.fit(np.array(training_set), np.array(training_set_result))
# joblib.dump(forest, 'RandomForrest.pkl') 
# forest = joblib.load('RandomForrest.pkl')

# nn = MLPClassifier(algorithm='l-bfgs', alpha=1e-5, hidden_layer_sizes=(100, 20, 10), random_state=100, max_iter=10000)
# nn = nn.fit(np.array(training_set), np.array(training_set_result))

small_chunk_num = 20
chunk_length = len(testing_set)/ small_chunk_num
for chunk_index in range(small_chunk_num - 1):

	output = forest.predict(np.array(testing_set[chunk_index * chunk_length: (chunk_index + 1) * chunk_length]))
	evaluate_output(output, testing_set_result_all[chunk_index * chunk_length: (chunk_index + 1) * chunk_length])

	output_proba = forest.predict_proba(np.array(testing_set[chunk_index * chunk_length: (chunk_index + 1) * chunk_length]))

	evaluate_proba_output(output, output_proba, testing_set_result_all[chunk_index * chunk_length: (chunk_index + 1) * chunk_length], 0)
	evaluate_proba_output(output, output_proba, testing_set_result_all[chunk_index * chunk_length: (chunk_index + 1) * chunk_length], 0.6)
	evaluate_proba_output(output, output_proba, testing_set_result_all[chunk_index * chunk_length: (chunk_index + 1) * chunk_length], 0.7)
	evaluate_proba_output(output, output_proba, testing_set_result_all[chunk_index * chunk_length: (chunk_index + 1) * chunk_length], 0.8)
	evaluate_proba_output(output, output_proba, testing_set_result_all[chunk_index * chunk_length: (chunk_index + 1) * chunk_length], 0.9)
	print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
