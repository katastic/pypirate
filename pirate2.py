#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup 
import re
import datetime
from prettytable import PrettyTable 

import sqlite3
c = sqlite3.connect('test2.db')

# https://thepiratebay10.org/top/all
# https://thepiratebay10.org/top/100
# 100 audio
# 200 video
# 300 applications
# 400 games
# 500 porn
# 600 other [ebooks, physicals, etc]
sections = ["all", "100", "200", "300", "400","500", "600"]

for sect in sections:
	url = "https://thepiratebay10.org/top/{0}".format(sect) 
	print(url)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	t = PrettyTable()
	t.field_names = ["Name", "Seeds", "Leeches", "Date Time", "Size", "Size (bytes)"]

	capture_datetime = datetime.datetime.now().strftime("%m-%d-%Y %H:%M")

	for i in range(1,101):
		ROW = i

		name = soup.find("table").find_all("tr")[ROW].find_all("td")[1].find("a", {"class":"detLink"}).text
		date_size_uploader_string = soup.find("table").find_all("tr")[ROW].find_all("td")[1].find("font", {"class":"detDesc"}).text
		#data = soup.find("table").find_all("tr")[1].find_all("td")[1]
		seeds = soup.find("table").find_all("tr")[ROW].find_all("td")[2].text
		leeches = soup.find("table").find_all("tr")[ROW].find_all("td")[3].text

		#print("name:",name)
		#print("seeds:", seeds)
		#print("leeches:", leeches)
		x = date_size_uploader_string.split(",")
		size = x[1][ x[1].find('Size ')+5 : ]
		uploaded_date = x[0][ x[0].find('Uploaded ')+9 : ]

		raw_size = -1
		if "KiB" in size:
			value = size[ :str.find("KiB", size)-3 ]
			raw_size = float(value)*1024
			#print(value, " ", size)
		if "MiB" in size:
			value = size[ :str.find("MiB", size)-3 ]
			raw_size = float(value)*1024*1024
			#print(value, " ", size)
		if "GiB" in size:
			value = size[ :str.find("GiB", size)-3 ]
			raw_size = float(value)*1024*1024*1024
			#print(value, " ", size)

		proper_datetime = uploaded_date

	#	print(uploaded_date)
		X = re.match(r'(\d\d-\d\d)\s(\d\d:\d\d)', uploaded_date)   #case: 02-02 23:23   (date time)
		if X is not None:
			date1 = X[1] + '-' + str(datetime.datetime.today().year) 
			time1 = X[2]
	#		print(date1, time1, sep=",")
			proper_datetime = date1 + " " + time1;

		X = re.match(r'(\d\d-\d\d)\s(\d\d\d\d)', uploaded_date) 	#case: 02-02 2015   (mm-dd year)
		if X is not None:
			date1 = X[1] + '-' + X[2] + ' 00:00' #no time data, so fill in 0's
			proper_datetime = date1

	#	print(uploaded_date)
		if uploaded_date.startswith('Y-day'):#case: Y-day 23:23
			idx = uploaded_date.find('Y-day')
			after = uploaded_date[ idx+4: ]
			td = datetime.datetime.today()
			day = td.day
			month = td.month
			year = td.year
			
			#WARNING, this will FAIL if the FETCH DATE is the 1st, but YESTERDAY is 1st-1 = 0!
			#BUG ------------------------------------------------------------------------------
			#0 pad months less than 10   ala 08/12/12
			if month < 10: 
				the_date = '0' + str(month) + '-' + str(day-1) + '-' + str(year)
			else:
				the_date = str(month) + '-' + str(day-1) + '-' + str(year)
			
			the_time = uploaded_date[6:]
			uploaded_date = the_date + " " + the_time
	#		print(uploaded_date)
			proper_datetime = uploaded_date

		if uploaded_date.startswith('Today'):#case: Today 03:23
			idx = uploaded_date.find('Today')
			after = uploaded_date[ idx+5: ]
			td = datetime.datetime.today()
			day = td.day
			month = td.month
			year = td.year
			if month < 10: #0 pad months less than 10   ala 08/12/12
				the_date = '0' + str(month) + '-' + str(day) + '-' + str(year)
			else:
				the_date = str(month) + '-' + str(day) + '-' + str(year)
			
			the_time = uploaded_date[6:]
			uploaded_date = the_date + " " + the_time
			proper_datetime = uploaded_date

		t.add_row([name, seeds, leeches, proper_datetime, size, raw_size])
				
		rank=i
		abc = "INSERT INTO data VALUES (NULL, '{0}', '{1}',{2},'{3}',{4},{5},'{6}','{7}')".format(sect, name.replace("'",""), rank, capture_datetime, seeds, leeches, proper_datetime, raw_size)
		c.execute(abc)
		c.commit()
	
	print(t)
	t.clear_rows()
	print("Results for section ", sect, "for datetime: ",  capture_datetime)
c.close()

