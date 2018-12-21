api_key = 'RGAPI-cf71c9ca-d422-4637-ba9e-79a89b884e9d'
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
