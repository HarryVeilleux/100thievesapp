api_key = 'RGAPI-2dc8b901-7393-47c0-94e1-ad170ec11e11'
reg = 'na1'

# get champions dictionary
import csv
with open('thieves/data/champs.csv', 'r') as file:
    reader = csv.reader(file)
    champions = {row[0]:row[1] for row in reader}

# get pros dictionary
import datetime as dt
today = dt.date.today().strftime('%Y%m%d')
with open('thieves/data/pros.csv', 'r') as file:
    reader = csv.reader(file)
    pros = [[row[0],row[1],row[2],None,today] for row in reader]
