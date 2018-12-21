from riotwatcher import RiotWatcher
from math import ceil
import sqlite3
from .data.base import api_key, reg, today
from requests import HTTPError
import pandas as pd
import datetime as dt
import time

class User(object):
    def __init__(self, accountID, con):
        self.accountID = accountID
        self.api_key = api_key
        self.watcher = RiotWatcher(api_key)
        self.reg = reg
        self.today = today
        self.con = con
        self.cur = con.cursor()

    def utodb(self, acctID, player=''):
        """ Write user to accounts table as known account. """
        con = self.con
        cur = con.cursor()

        try:
            cur.execute(f"SELECT * FROM accounts WHERE AccountID={acctID}").fetchall()[0]
            toupdate = input(f"Account {acctID} already in database. Update information? (Y/N) ")
            if toupdate.lower() == 'n':
                return con, cur
        except IndexError:
            pass

        while True:
            try:
                summ = self.watcher.summoner.by_account(reg, acctID)
                name = summ['name']
            except HTTPError as err:
                if err.response.status_code == 429:
                    print('Too many requests, waiting 30 seconds...')
                    time.sleep(30)
                    continue
                elif err.response.status_code == 404:
                    print(f'No results for account {acctID}.')
                    name = 'UNKNOWN NAME'
                    break
                elif err.response.status_code == 503:
                    print('Server delay, retrying...')
                    continue
                else:
                    raise
            break
        cur.execute(f"INSERT INTO accounts VALUES ({acctID}, '{name}', '{player}', '{self.today}')")
        if player != '':
            print(f"Summoner {name} has been added to database as an account belonging to {player}.")
        else:
            print(f"Summoner {acctID} added to database with no player.")
        return con, cur

    def updatedb(self, month):
        """ Update database with info for accountID and given month. """
        watcher = self.watcher
        acctID = self.accountID
        reg = self.reg
        con = self.con
        cur = con.cursor()
        # get iters
        epoch = dt.datetime.utcfromtimestamp(0)
        def datetoepoch(month):
            ms = int((dt.datetime(2018,month,1)-epoch).total_seconds() * 1000)
            return ms
        def epochtodate(ms):
            ymdhms = dt.datetime.fromtimestamp(ms/1000).strftime('%Y%m%d %H:%M:%S')
            return ymdhms
        stime = datetoepoch(month)
        etime = datetoepoch(month + 1)
        mswk = int(7 * 24 * 60 * 60 * 1000)
        iters = ceil((etime - stime) / mswk)
        diffs = int(round((etime - stime) / iters))
        # get gameIDs
        tot_matches = 0
        tot_players = 0
        gamerows = []
        plrows = []
        for i in range(1,iters + 1):
            while True:
                try:
                    stime += (diffs*(i-1))
                    matches = watcher.match.matchlist_by_account(reg,acctID,queue=420,
                        begin_time=stime,end_time=stime+diffs)
                    gameIDs = [match['gameId'] for match in matches['matches']]
                    # filter out IDs already in db
                    def list_to_filter(flist):
                        filter = "("
                        for item in flist:
                            filter += (str(item) + ",")
                        filter = filter[0:-1] + ")"
                        return filter

                    # select all gameIDs in match db and remove cached matches from list
                    idlist = list_to_filter(gameIDs)
                    cur.execute(f"SELECT GameID FROM matches WHERE GameID IN {idlist}")
                    cached = [int(el[0]) for el in cur.fetchall()]
                    newgames = [id for id in gameIDs if id not in cached]
                    print(f"{len(cached)} cached games found.")
                    cont = input(f"{len(newgames)} new games found for segment {i} of {iters} (Press Enter)")

                    # get info for games from watcher
                    if len(newgames) > 0:
                        for game in newgames:
                            print(f"Getting data for game {game}...")
                            while True:
                                try:
                                    match = watcher.match.by_id(reg,game)
                                except HTTPError as err:
                                    if err.response.status_code == 429:
                                        print('Too many requests, waiting 30 seconds...')
                                        time.sleep(30)
                                        continue
                                    elif err.response.status_code == 404:
                                        print(f'No results for game {game}. Major error.')
                                    elif err.response.status_code == 503:
                                        print('Server delay, retrying...')
                                        continue
                                    else:
                                        raise
                                break

                            gamerow = [game, epochtodate(match['gameCreation']),
                                epochtodate(match['gameCreation'] + match['gameDuration']), match['gameVersion'],
                                next(team['teamId'] for team in match['teams'] if team['win']=='Win')]
                            plIds = []
                            for pl in match['participantIdentities']:
                                gamerow.append(pl['player']['accountId'])
                                plIds.append(pl['player']['accountId'])
                            gamerows.append(gamerow)
                            for pl in match['participants']:
                                plrow = [str(game) + '-' + str(plIds[pl['participantId']-1]),
                                    game, plIds[pl['participantId']-1], pl['stats']['win'],
                                    pl['championId'], pl['teamId'], pl['stats']['kills'],
                                    pl['stats']['deaths'], pl['stats']['assists'],
                                    pl['stats']['totalMinionsKilled'], pl['stats']['visionScore'],
                                    pl['stats']['wardsKilled'], pl['stats']['goldEarned']]
                                plrows.append(plrow)

                except HTTPError as err:
                    if err.response.status_code == 429:
                        print('Too many requests, waiting 30 seconds...')
                        time.sleep(30)
                        continue
                    elif err.response.status_code == 404:
                        print(f'No results for time range {i}!')
                        break
                    elif err.response.status_code == 503:
                        print('Server delay, retrying...')
                        continue
                    else:
                        raise
                break

        # write data to db
        print(f"Writing {len(gamerows)} games to cache.")
        tot_matches += len(gamerows)
        cur.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",gamerows)

        print(f"Writing {len(plrows)} players to cache.")
        tot_players += len(plrows)
        cur.executemany("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",plrows)

        print(f"Update complete. {tot_matches} rows added to match cache; {tot_players} rows added to player cache.")
        con.commit()
        return con, cur

    def getinfo(self, month, update=True):
        """ Get 10 most played with accounts and match data for month. """
        if update==True:
            # update from watcher
            con, cur = self.updatedb(month)
        else:
            con, cur = self.con, self.cur

        # sqls for match info, played-with info
        games_sql = f"SELECT * FROM players WHERE AccountID={self.accountID}"
        team_sql = sql = f"""
            SELECT CASE
                  WHEN {self.accountID} IN (Play1, Play2, Play3, Play4, Play5)
                    THEN Play1 || ',' || Play2 || ',' || Play3 || ',' || Play4 || ',' || Play5
                  ELSE Play6 || ',' || Play7 || ',' || Play8 || ',' || Play9 || ',' || Play10
                  END team
             FROM matches"""
        # get played-with
        teamres = cur.execute(sql).fetchall()
        teammates = [row[0].split(',') for row in teamres]
        plwd = {}
        for game in teammates:
            for acct in game:
                try:
                    plwd[str(acct)] += 1
                except KeyError:
                    plwd[str(acct)] = 1
        plwds = sorted(plwd.items(), key=lambda kv: kv[1], reverse=True)

        # get game data and aggregate
        gamesdf = pd.read_sql(games_sql, self.con)
        #agghead = ['Name', 'Games', '']
        #aggdict = {}

        topplw = []
        for acct in plwds[1:10]:
            # convert played-with IDs to names and save to list
            try:
                cur.execute(f"SELECT SummonerName FROM accounts WHERE AccountID={int(acct[0])}")
                name = cur.fetchone()[0]
            except TypeError:
                print(f'Account {acct[0]} not in database, getting summoner name...')
                con, cur = self.utodb(int(acct[0]))
                cur.execute(f"SELECT SummonerName FROM accounts WHERE AccountID={int(acct[0])}")
                name = cur.fetchone()[0]
            topplw.append((name, acct[1]))
        return con, cur, topplw, gamesdf

    def viewinfo(self, month):
        """ Pretty print data on summoner for given month. """
        con, cur, topplw, gamesdf = self.getinfo(month, update=False)
        cur.execute(f"SELECT SummonerName FROM accounts WHERE AccountID={self.accountID}")
        name = cur.fetchone()[0]
        print("Top 10 summoners played with:")
        for rec in topplw:
            print(rec[0] + '-' + str(rec[1]))

        print("\nAggregated match data:")
        agghead = ['Name', 'Games', 'Wins', 'Kills', 'Deaths', 'Assists']
        aggdata = [name, gamesdf['Key'].count(), sum(gamesdf['Win']),
            sum(gamesdf['Kills']), sum(gamesdf['Deaths']), sum(gamesdf['Assists'])]

        for head in agghead:
            print(head, end='\t')
        print('\n')

        for point in aggdata:
            print(str(point), end='\t')
