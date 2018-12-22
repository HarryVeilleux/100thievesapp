import sqlite3
from sqlite3 import OperationalError
import datetime as dt
import pandas as pd

class Dbquery(object):
    """ Query given database """
    def __init__(self, dbname):
        self.dbname = dbname
        self.con = sqlite3.connect('thieves/data/' + self.dbname + '.db')

    def db_exist(self):
        """ Check if database already exists. """
        try:
            cur = self.con.cursor()
            cur.execute("""CREATE TABLE accounts
                (AccountID, SummonerName, Player, LastUpdate)""")
            self.con.close()
            return False
        except OperationalError:
            self.con.close()
            return True

    def acct_from_db(self, summ, open=False):
        """ Get account information from summoner name or 1 if not in database. """
        sql = f"SELECT * FROM accounts WHERE SummonerName='{summ}'"
        cur = self.con.cursor()
        row = cur.execute(sql).fetchone()
        if open==False:
            self.con.close()

        if row is None:
            return 1
        else:
            return row

    def summ_from_db(self, acctID, open=False):
        """ Get summoner name from account ID or 1 if not in database. """
        sql = f"SELECT SummonerName FROM accounts WHERE AccountID={acctID}"
        cur = self.con.cursor()
        try:
            name = cur.execute(sql).fetchone()[0]
            if open==False:
                self.con.close()
            return name

        except TypeError:
            if open==False:
                self.con.close()
            return 1

    def gameids(self, acctID):
        """ Get list of gameIDs or 1 if not in database. """
        sql = f"""SELECT GameID FROM matches
             WHERE {acctID} IN (Play1, Play2, Play3, Play4, Play5, Play6, Play7, Play8, Play9, Play10)"""
        cur = self.con.cursor()
        ids = cur.execute(sql).fetchall()
        self.con.close()

        gameIDs = [id[0] for id in ids]

        return gameIDs

    def plw_in_range(self, summ, start=None, end=None):
        """ Get list of accounts played within date range or 1 if not in database. """
        try:
            acctID = self.acct_from_db(summ, open=True)[0]
        except TypeError:
            return 1

        if start is None:
            sqlstart = 0
        else:
            sqlstart = int(start.strftime('%Y%m%d'))

        if end is None:
            sqlend = 100000000
        else:
            sqlend = int(end.strftime('%Y%m%d'))

        sql = f"""
            SELECT CASE
                  WHEN {acctID} IN (Play1, Play2, Play3, Play4, Play5)
                    THEN Play1 || ',' || Play2 || ',' || Play3 || ',' || Play4 || ',' || Play5
                  ELSE Play6 || ',' || Play7 || ',' || Play8 || ',' || Play9 || ',' || Play10
                  END team
             FROM matches
             WHERE CAST(SUBSTR(Start,1,8) AS INTEGER) BETWEEN {sqlstart} AND {sqlend}
                AND {acctID} IN (Play1, Play2, Play3, Play4, Play5, Play6, Play7, Play8, Play9, Play10)"""
        cur = self.con.cursor()

        # get played-with list of sorted tuples
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

        topplw = []
        for acct in plwds[1:11]:
            # convert played-with IDs to names and save to list
            name = self.summ_from_db(int(acct[0]),open=True)
            if name == 1:
                name = 'UNKNOWN PLAYER'
            topplw.append((name, acct[0], acct[1]))
        self.con.close()

        return topplw

    def matches_in_range(self, summ, start=None, end=None):
        """ Get dataframe of accounts played within date range or 1 if not in database. """
        try:
            acctID = self.acct_from_db(summ, open=True)[0]
        except TypeError:
            return 1

        if start is None:
            sqlstart = 0
        else:
            sqlstart = int(start.strftime('%Y%m%d'))

        if end is None:
            sqlend = 100000000
        else:
            sqlend = int(end.strftime('%Y%m%d'))

        sql = f"""
            SELECT p.*
            FROM players p
              JOIN matches m ON p.GameID = m.GameID
            WHERE p.AccountID={acctID}
              AND CAST(SUBSTR(m.Start,1,8) AS INTEGER) BETWEEN {sqlstart} AND {sqlend}"""

        gamesdf = pd.read_sql(sql, self.con)
        self.con.close()

        return gamesdf
