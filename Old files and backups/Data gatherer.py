#!/usr/bin/env python

# Data scrapper.
# Version 0.1
# Christophe Foyer - 2016


import xlwt
from xlrd import open_workbook
from datetime import datetime
import forecastio

#don't forget to put in your forecast.io API key, you can either use the prompt or enter it directly
#api_key = "your API key"
api_key = input("Enter your forecast.io API key")

#set filename:

filename = 'Wheat-price-data.xlsx'

#styles:

style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
    num_format_str='#,##0.00')
style1 = xlwt.easyxf(num_format_str='D-MMM-YY')



