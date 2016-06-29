#!/usr/bin/env python

# Wheat price prediction using Baysian classification.
# Version 1.0
# Christophe Foyer - 2006

#Special thanks to Machine Learning Mastery
#http://machinelearningmastery.com/naive-bayes-classifier-scratch-python/

from xlrd import open_workbook
import random
import math

#set filename:

filename = 'Wheat-price-data.xlsx'

#import wheat price data (will automate downloading later, probably a different script that write to the excel file)

def importExcel(filename):
    #this function is a very ugly, and not that effecient. but it should work...
    excel = open_workbook(filename)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_day_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    leap_years = [1900, 1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968, 1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024, 2028, 2032, 2036, 2040, 2044, 2048, 2052, 2056, 2060, 2064, 2068, 2072, 2076, 2080, 2084, 2088, 2092, 2096]
    #extract data from excel sheet
    for sheet in excel.sheets():
        number_of_rows = sheet.nrows
        number_of_columns = sheet.ncols
        dataset = [[]]*(number_of_columns + 2)
        date = []
        date_string = []
        price = []
        rows = []
        #this method is already obsolete (since it's less accurate and doesn't use the same format)
        #but since it works for things that may not be typed in correctly it might help in case of user error
        for row in range(1, number_of_rows):
            #excel stores dates as the number of days since 1900-Jan-0 (not sure if that means january 1st or december 31st but that won't matter much in our case)
            #new method: substract number of days in year until negative
            days = float(date_string)
            i = 0
            leap = 0
            #this will find how many years and how many leftover days for that year
            while days >= (365 + leap):
                leap = 0
                if i + 1900 in leap_years:
                    leap = 1
                days = days - 365 - leap
                i = i + 1
            year = i
            #now find the month and leftover days given leftover days
            month = 1
            for i in range(1, 12):
                #for debugging
                #if year + 1900 == 1998:
                #    print days, month ,year
                ##############
                if (year + 1900 in leap_years) and (i == 2):
                     leap = 1
                else:
                     leap = 0
                if days <= (month_day_count[i-1] + leap):
                    break
                else:
                    days = days - month_day_count[i-1] - leap
                    month = i + 1
            #now we should have the exact date seperated in day, month and year
            if (year + 1900 in leap_years):
                     leap = 1
                else:
                     leap = 0
            #different format, easier to use decimals
            #date_new = int(days), int(month), int(year+1900),
            date_new = (year + 1900) + month / 12 + days /(365 + leap)
            date.append(date_new)
            dataset[1].append(year)
            dataset[2].append(month)
            dataset[3].append(days)
                
            value  = (sheet.cell(row,1).value)
            try:
                value = str(int(value))
            except ValueError:
                dataset[4].append('unknown')
                pass
            finally:
                dataset[4].append(value)
                
            #now the rest of the data
            for col in range(2, number_of_columns):
                value  = (sheet.cell(row,col).value)
                try:
                    value = str(int(value))
                except ValueError:
                    dataset[col + 2].append('unknown')
                    pass
                finally:
                    dataset[col + 2].append(value)
            #now all the data should be accessible from the "dataset" array
    return dataset

def splitDataset(dataset, splitRatio):
	trainSize = int(len(dataset) * splitRatio)
	trainSet = []
	copy = list(dataset)
	while len(trainSet) < trainSize:
		index = random.randrange(len(copy))
		trainSet.append(copy.pop(index))
	return [trainSet, copy]

def separateByClass(dataset):
	separated = {}
	for i in range(len(dataset)):
		vector = dataset[i]
		if (round(vector[4]) not in separated):
			separated[round(vector[4])] = []
		separated[round(vector[4])].append(vector)
	return separated

def mean(numbers):
	return sum(numbers)/float(len(numbers))

def stdev(numbers):
	avg = mean(numbers)
	variance = sum([pow(x-avg,2) for x in numbers])/float(len(numbers)-1)
	return math.sqrt(variance)

def summarize(dataset):
	summaries = [(mean(attribute), stdev(attribute)) for attribute in zip(*dataset)]
	del summaries[4]
	return summaries

def summarizeByClass(dataset):
	separated = separateByClass(dataset)
	summaries = {}
	for classValue, instances in separated.iteritems():
		summaries[classValue] = summarize(instances)
	return summaries

def calculateProbability(x, mean, stdev):
	exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
	return (1 / (math.sqrt(2*math.pi) * stdev)) * exponent

def calculateClassProbabilities(summaries, inputVector):
	probabilities = {}
	for classValue, classSummaries in summaries.iteritems():
		probabilities[classValue] = 1
		for i in range(len(classSummaries)):
			mean, stdev = classSummaries[i]
			x = inputVector[i]
			probabilities[classValue] *= calculateProbability(x, mean, stdev)
	return probabilities

def predict(summaries, inputVector):
	probabilities = calculateClassProbabilities(summaries, inputVector)
	bestLabel, bestProb = None, -1
	for classValue, probability in probabilities.iteritems():
		if bestLabel is None or probability > bestProb:
			bestProb = probability
			bestLabel = classValue
	return bestLabel

def getPredictions(summaries, testSet):
	predictions = []
	for i in range(len(testSet)):
		result = predict(summaries, testSet[i])
		predictions.append(result)
	return predictions

def getAccuracy(testSet, predictions):
	correct = 0
	for i in range(len(testSet)):
		if testSet[i][-1] == predictions[i]:
			correct += 1
	return (correct/float(len(testSet))) * 100.0

def main():
	splitRatio = 0.67
	dataset = importExcel(filename)
	print('Loaded data file {0} with {1} rows').format(filename, len(dataset))
	trainingSet, testSet = splitDataset(dataset, splitRatio)
	print('Split {0} rows into train={1} and test={2} rows').format(len(dataset), len(trainingSet), len(testSet))
	# prepare model
	summaries = summarizeByClass(trainingSet)
	# test model
	predictions = getPredictions(summaries, testSet)
	accuracy = getAccuracy(testSet, predictions)
	print('Accuracy: {0}%').format(accuracy)
 
main()
