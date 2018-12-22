from smurf import Smurffinder
from time import clock
from math import floor
import datetime as dt

summoners = ['Fox FeniX']

smurf = Smurffinder()
smurf.dbname = 'master'

whole_starts = clock()

for summoner in summoners:
    this_starts = clock()
    print(f"Gathering data for {summoner}...")
    info = smurf.dbquery(smurf.dbname).acct_from_db(summoner)
    plinfo = smurf.riotdata().summ_info(summoner)
    smurf.dbupdate(smurf.dbname).update_accounts(plinfo, player='No')
    smurf.start = dt.datetime.strptime('2018/06/01', '%Y/%m/%d')
    smurf.end = dt.datetime.strptime('2018/12/01', '%Y/%m/%d')
    acctID = smurf.dbquery(smurf.dbname).acct_from_db(summoner)[0]
    cached = smurf.dbquery(smurf.dbname).gameids(acctID)
    gamerows, plrows, allpls = smurf.riotdata().match_in_range(
        summoner, smurf.start, smurf.end, cached=cached)
    smurf.dbupdate(smurf.dbname).update_matches(gamerows)
    smurf.dbupdate(smurf.dbname).update_players(plrows)
    this_ends = clock()
    diffs = this_ends - this_starts
    h = floor(diffs / 3600)
    m = floor((diffs - h * 3600) / 60)
    s = floor(diffs - h * 3600 - m * 60)
    print(f'Run time for {summoner}: ' + str(h) + 'h ' + str(m) + 'm ' + str(s) + 's')

whole_ends = clock()
diffs = whole_ends - whole_starts
h = floor(diffs / 3600)
m = floor((diffs - h * 3600) / 60)
s = floor(diffs - h * 3600 - m * 60)
print('Total run time: ' + str(h) + 'h ' + str(m) + 'm ' + str(s) + 's')
