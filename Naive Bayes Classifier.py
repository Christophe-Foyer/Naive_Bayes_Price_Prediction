#!/usr/bin/env python

# Wheat price prediction using Baysian classification.
# Version 1.0
# Christophe Foyer - 2016


from xlrd import open_workbook
import random
import math
import copy

#set filename:

filename = 'Wheat-price-data.xlsx'

# import wheat price data
# (will automate downloading later, probably a separate
# script that writes to the excel file)

def importExcel(filename, rounding):
    #this function is a very ugly, but for now it does the job
    excel = open_workbook(filename)
    #extract data from excel sheet
    for sheet in excel.sheets():
        number_of_rows = sheet.nrows
        number_of_columns = sheet.ncols
        dataset = [[0.0 for x in range(number_of_columns + 3)] for y in range(number_of_rows)]
        date = []
        date_string = []
        price = []
        rows = []
        for row in range(1, number_of_rows):
                #excel stores dates as the number of days since 1900-Jan-0 (not sure if that means january 1st or december 31st but that won't matter much in our case)
                #new method: substract number of days in year until negative
                date_string  = str(sheet.cell(row,0).value)
                days = float(date_string)
                dataset[row-1][0] = float(days)
                [dataset[row-1][1], dataset[row-1][2], dataset[row-1][3]] = excelDate(days)
                value  = (sheet.cell(row,1).value)
                try:
                    value = str(int(value))
                    dataset[row-1][4] = float(value)
                except ValueError:
                    pass
                finally:
                    dataset[row-1][4] = round(float(value)/rounding,0)*rounding

                #now the rest of the data
                for col in range(2, number_of_columns):
                    value  = (sheet.cell(row,col).value)
                    try:
                        dataset[row-1][col + 3] = float(value)
                    except ValueError:
                        pass
                #now all the data should be accessible from the "dataset" array
    del dataset[-1]
    #print dataset
    return dataset

def excelDate(days):
        month_day_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        leap_years = [1900, 1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968, 1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024, 2028, 2032, 2036, 2040, 2044, 2048, 2052, 2056, 2060, 2064, 2068, 2072, 2076, 2080, 2084, 2088, 2092, 2096]
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
        return [year, month, days]

def splitDataset(dataset, splitRatio):
	trainSize = int(len(dataset) * splitRatio)
	trainSet = []
	copy = list(dataset)
	while len(trainSet) < trainSize:
		index = random.randrange(len(copy))
		trainSet.append(copy.pop(index))
	return [trainSet, copy]

def separateByClass(dataset, rounding):
        #this might not be working correctly    
        separated = {}
        for i in range(len(dataset)):
                vector = dataset[i] 
                if (vector[0] not in separated):
                        separated[vector[0]] = {}
                for classValue, instances in vector[1].iteritems():
                        if (round(float(classValue)/rounding, 0)*rounding not in separated[vector[0]]):
                            separated[vector[0]][round(float(classValue)/rounding, 0)*rounding] = []
                        separated[vector[0]][round(float(classValue)/rounding, 0)*rounding].append(vector[1][classValue][0])
##                separated[vector[0]].append(vector[1])
##                if len(separated[vector[0]]) > 2:
##                    separated[vector[0]][1] = separated[vector[0]][1] + separated[vector[0]][2]
##                    del separated[vector[0]][2]
        #print separated[105]
        return separated

def mean(numbers):
        #remove unknowns from calculations
        if 'unknown' in numbers:
            numbers.remove('unknown')
        return sum(numbers)/float(len(numbers))

def stdev(numbers):
        #remove unknowns from calculations
        if 'unknown' in numbers:
            numbers.remove('unknown')
        if len(numbers) > 1:
            avg = mean(numbers)
            variance = sum([pow(x-avg,2) for x in numbers])/float(len(numbers)-1)
            return math.sqrt(variance)
        else:
            return 0

def summarize(dataset):
        summaries = [(mean(attribute), stdev(attribute)) for attribute in zip(*dataset)]
        return summaries

def summarizeByClass(dataset, rounding):
        separated = separateByClass(dataset, rounding)
        summaries = {}
        for price, instances in separated.iteritems():
            # print 'loaded price data for :', price
            for relativeDate, instances in separated[price].iteritems():
                if (price not in summaries):
                        summaries[price] = {}
                if (relativeDate not in summaries[price]):
                        summaries[price][relativeDate] = {}
                summaries[price][relativeDate] = summarize(separated[price][relativeDate])
        return summaries

def calculateProbability(x, mean, stdev):
        if stdev !=0 and (mean != 'unknown') and (stdev != 'unknown') and (x != 'unknown'):
            exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
            return (1 / (math.sqrt(2*math.pi) * stdev)) * exponent
        else:
            return 1

def calculateClassProbabilities(summaries, inputVector):
        #now this is where it breaks
        probabilities = {}
        #print summaries
        #print 'input vector', inputVector
        for price, classSummaries in summaries.iteritems():
                probabilities[price] = 1
                priceProbability = []
                #print 'data and stuff', summaries[classValue]
                for relativeDate, classSummaries in summaries[price].iteritems():
                        if relativeDate in inputVector[1]:
                                for i in range(len(classSummaries)):  #old stuff, to be deleted
                                        #print 'class', classSummaries #data
                                        #print price
                                        #print relativeDate
                                        classProbabilities = 1
                                        mean, stdev = classSummaries[i]
                                        #print inputVector[1][relativeDate][0]
                                        x = inputVector[1][relativeDate][0][i]
                                        classProbabilities *= calculateProbability(x, mean, stdev)
                                        priceProbability.append(classProbabilities)
                        else: #I still have to decide what to do if there's no corresponding data (pretty likely to happen)

                                #should regroup data within rounding parameters and test it for that data
                                #if there is no such data, then we should look for more data outside the rouding
                                #parameters (maybe linear regression between the two closest points? Maybe fit a curve to the data?)
                                
                                #for i in range(len(classSummaries)):
                                #    priceProbability.append(0.5)
                                
                                pass
                #print 'prob', priceProbability
                probabilities[price] *= priceProbability
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
		if testSet[i][0] == predictions[i]:
			correct += 1
	return (correct/float(len(testSet))) * 100.0

def reorganizeData(dataset):
        #this function reorganises the data for better classification, unfortunately given the drastic changes made to the code
        #to implement this new format, the data now has to be reorganized for the code to work
        reorganizedData = [["unknown"] for y in range(len(dataset))]
        for i in range(len(dataset)):
            reorganizedData[i] = [dataset[i][4]]
            listList = {}
            for j in range(len(dataset)):
                if dataset[i][0] >= dataset[j][0]:
                    vector = copy.deepcopy(dataset[j])
                    # round relative dates (reduces amount of classes)
                    # lower rounding means higher accuracy
                    vector[0] = dataset[i][0] - dataset[j][0]
                    if (vector[0] not in listList):
                            listList[vector[0]] = []
                    listList[vector[0]].append(vector)
            reorganizedData[i].append(listList)
        return reorganizedData

def createModel(rounding, roundingPrice):
        splitRatio = 0.67
        #rounding = 30 # days to approximate to (extends dataset)
        #roundingPrice = 10 # units to round to for the price column of the data
        dataset = importExcel(filename, roundingPrice)
        # reorganise data to include past days might include it in importEcel later
        dataset = reorganizeData(dataset)
        print('Loaded data file {0} with {1} rows').format(filename, len(dataset))
        trainingSet, testSet = splitDataset(dataset, splitRatio)
        print('Split {0} rows into train={1} and test={2} rows').format(len(dataset), len(trainingSet), len(testSet))
        print('Rounding prices to {0} units, and dates to {1} days').format(roundingPrice, rounding)
        # prepare model
        print('Preparing model...')
        summaries = summarizeByClass(trainingSet, rounding)
        # test model
        predictions = getPredictions(summaries, testSet)
        print('Testing model...')
        accuracy = getAccuracy(testSet, predictions)
        print('Accuracy: {0}%').format(accuracy)
        #this snipet of code returns a prediction
        #inputVector = [36100.0, 98, 11, 1.0, 1.0, 111.77, 0.04575224550898204]
        #prediction = getPredictions(summaries, reorganizeData([inputVector]))
        #print prediction
        return [accuracy, summaries]

def testAccuracy(iterations, rounding, roundingPrice):
        [averageAccuracy, summaries] = createModel(rounding, roundingPrice)
        for i in range(iterations - 1):
            [accuracy, summaries] = createModel(rounding, roundingPrice)
            averageAccuracy = (averageAccuracy*i+accuracy)/(i+1)
        print('Average Accuracy: {0}%').format(averageAccuracy)
        return averageAccuracy

def findBestSettings(testRange, numberOfTests):
        accuracy = []
        bestAccuracy = [0, 0]
        roundingPrice = 1
        for i in range(testRange[0], testRange[1]):
            print "rounding to", i, "days"
            accuracy.append(testAccuracy(numberOfTests, i, roundingPrice))
            if accuracy[i - 1 - testRange[0]] > bestAccuracy[0]:
                bestAccuracy = [accuracy[i - 1 - testRange[0]], i]
        print "accuracy", accuracy
        print "best", bestAccuracy
        #69 is the best setting for now (7.7% average accuracy)


#this snipet of code returns a prediction
def makePrediction(inputVector):
    #if no data, write unknown, same format as in the file
    prediction = getPredictions(summaries, reorganizeData([inputVector]))
    print prediction

[averageAccuracy, summaries] = createModel(1, 10)
#example format:
#inputVector = [36100.0, 98, 11, 1.0, 111.77, 0.04575224550898204]
#if no date is given, put a placeholder date anyways (it's how it organises things, might fix later)
inputVector = [36100.0, 98, 11, 1.0, "unknown", 0.04575224550898204]
makePrediction(inputVector)        
#findBestSettings([1, 100], 15)

