from riotwatcher import RiotWatcher
import csv
import sqlite3
from .data.base import api_key, champions, pros, reg
from requests import HTTPError
from .user import User

class Finder(object):
    def __init__(self):
        self.api_key = api_key
        self.champions = champions
        self.pros = pros
        self.reg = reg
        self.watcher = RiotWatcher(api_key)

    def new_db(self):
        dbname = input("New database name: ")
        # create new db
        con = sqlite3.connect('thieves/data/' + dbname + '.db')
        cur = con.cursor()
        try:
            # create tables accounts, matches, players, pros
            cur.execute("""CREATE TABLE accounts
                (AccountID, SummonerName, Player, LastUpdate)""")
            cur.execute("""CREATE TABLE matches
                (GameID, Start, End, Patch, Winner, Play1, Play2, Play3, Play4, Play5,
                 Play6, Play7, Play8, Play9, Play10)""")
            cur.execute("""CREATE TABLE players
                (Key, GameID, AccountID, Win, Champion, Team, Kills, Deaths, Assists, CS,
                 Vision, WardsKilled, Gold)""")
            cur.execute("""CREATE TABLE pros
                (Player, Team, Position, Accounts, LastUpdate)""")
            # write base data to pros table
            cur.executemany("INSERT INTO pros VALUES (?, ?, ?, ?, ?)", pros)

            return con, cur
        except:
            cur.close()
            con.close()
            raise

    def from_db(self):
        # create db connection
        try:
            con = sqlite3.connect('thieves/data/master.db')
            cur = con.cursor()
            return con, cur
        except:
            raise

    def smurf(self, con, cur, summoner=None, accountID=None):
        if summoner is None:
            summoner = input("Summoner name: ")

        if accountID is None:
            # get accountID from db or watcher
            try:
                cur.execute(f"SELECT AccountID FROM accounts WHERE SummonerName='{summoner}'")
                accountID = int(cur.fetchone()[0])
            except TypeError:
                print(f"{summoner} not found in database. Fetching from Riot API...")
                while True:
                    try:
                        summ = self.watcher.summoner.by_name(reg, summoner)
                        accountID = summ['accountId']
                    except HTTPError as err:
                        if err.response.status_code == 429:
                            print('Too many requests, waiting 30 seconds...')
                            time.sleep(30)
                            continue
                        elif err.response.status_code == 404:
                            print(f'No results for summoner {summoner}!')
                            return
                        elif err.response.status_code == 503:
                            print('Server delay, retrying...')
                            continue
                        else:
                            raise
                    break

        return User(accountID, con)
