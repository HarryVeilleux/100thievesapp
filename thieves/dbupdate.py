import sqlite3
import datetime as dt
from .data.base import pros

class Dbupdate(object):
    """ Update database with information from Riot API. """
    def __init__(self, dbname):
        self.dbname = dbname
        self.con = sqlite3.connect('thieves/data/' + dbname + '.db')

    def create_db(self):
        """ Create new db file. """
        cur = self.con.cursor()
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
        self.con.commit()
        self.con.close()

    def update_accounts(self, acct_row, player=None):
        """ Add account to accounts table. """
        cur = self.con.cursor()
        if player!='No' and acct_row[2] is None:
            acct_row[2] = input(f'Player name for summoner {acct_row[1]} (enter if unknown): ')

        cur.execute(f"""INSERT INTO accounts
            VALUES ({acct_row[0]}, '{acct_row[1]}', '{acct_row[2]}', {acct_row[3]})""")
        self.con.commit()
        self.con.close()

    def update_matches(self, gamerows):
        """ Add match information to matches table. """
        cur = self.con.cursor()
        print(f"Writing {len(gamerows)} games to cache.")
        cur.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",gamerows)
        self.con.commit()
        self.con.close()

    def update_players(self, plrows):
        """ Add player match information to players table. """
        cur = self.con.cursor()
        print(f"Writing {len(plrows)} players to cache.")
        cur.executemany("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",plrows)
        self.con.commit()
        self.con.close()
