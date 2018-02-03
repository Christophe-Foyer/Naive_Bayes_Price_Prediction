#!/usr/bin/env python

# Wheat price prediction using Baysian classification.
# Version 1.0
# Christophe Foyer - 2006

from xlrd import open_workbook

#import wheat price data (will automate downloading later)

excel = open_workbook('Wheat-price-data.xlsx')
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_day_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#a list of leap years, we could add more but I doubt this code will be used for that long in its current form
leap_years = [1900, 1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968, 1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024, 2028, 2032, 2036, 2040, 2044, 2048, 2052, 2056, 2060, 2064, 2068, 2072, 2076, 2080, 2084, 2088, 2092, 2096]

#should probably add more data to excel sheet when it boots up (weather in different regions, wheat prices ect)
#good data would probably be weather, flour consumption, wheat production, and wheat price (obviously)

print "loaded"

#extract data from excel sheet
for sheet in excel.sheets():
    number_of_rows = sheet.nrows
    number_of_columns = sheet.ncols
    data = [[]]*number_of_rows
    print data
    date = []
    date_string = []
    date = []
    price = []
    rows = []
    status = "content"
    #this method is already obsolete (since it's less accurate and doesn't use the same format)
    #but since it works for things that may not be typed in correctly it might help in case of user error
    for row in range(1, number_of_rows):
        date_string  = str(sheet.cell(row,0).value)
        #print "raw-data:", date_string
        #compare string with month list
        for i in range (1, 12):
            #check each month
            set1 = []
            set2 = []
            for j in range (0, len(months[i])):
                set1.append(date_string[j])
                set2.append(months[i][j])
            #print set1
            #print set2
            if set1 == set2:
                month = i
		#print "length",len(date_string)
                year = int(date_string[len(date_string)-4])*1000+int(date_string[len(date_string)-3])*100+int(date_string[len(date_string)-2])*10+int(date_string[len(date_string)-1])
                date_new = month, year
                date.append(str(date_new))
                #print "date=", date_new
                status = "content"
                break
            else:
                status = "not happy"
                #print "not happy"
        if status == "not happy":
            #apparently some have different formats
            #excel stores dates as the number of days since 1900-Jan-0 (not sure if that means january 1st or december 31st but that won't matter much in our case)
            #year = round((float(date_string)-30)/365.25-0.5)+1900 #this kind of works just because it's monthly and tweeked so it works... should make it better            month = round((float(date_string)-(year-1900)*365)/30-1.5) #again, not exact but we can fix this later if we find better data
            #date_new = int(month), int(year)
            #date.append(str(date_new))

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
            date_new = int(days), int(month), int(year+1900),
            date.append(date_new)
            
        value  = (sheet.cell(row,1).value)
        try:
            value = str(float(value))
        except ValueError:
            pass
        finally:
            price.append(value)

        #now the rest of the data
        for col in range(2, number_of_columns):
            value  = (sheet.cell(row,col).value)
            try:
                value = str(float(value))
            except ValueError:
                pass
            finally:
                data[row-1] = value
        #now all the data should be accessible from the "data" array
    print data
    #this just prints data
    for i in range (0, len(date)):
        print " date: ", date[i], " prix: ", price[i], " Data: ", data[i][0:-1]

#data processing works it seems, should work with daily accuracy if specified now.
#now I need to find a way to automatically download weather data and if possible
#also wheat data every day (recieve transefer email using gmail autotransfer?)

#only then can I start using bayesian classification since the month of the year is
#obviously not enough data (otherwise it would be somewhat periodic which it is not
#the case)

