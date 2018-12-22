from thieves.dbquery import Dbquery
from thieves.dbupdate import Dbupdate
from thieves.viewdata import Viewdata
from thieves.riotdata import Riotdata
from sqlite3 import OperationalError
import datetime as dt

class Smurffinder(object):
    def __init__(self):
        self.summoner = None
        self.start = None
        self.end = None

    def dbquery(self, dbname):
        return Dbquery(dbname)

    def dbupdate(self, dbname):
        return Dbupdate(dbname)

    def viewdata(self):
        return Viewdata()

    def riotdata(self):
        return Riotdata()

    def screens(self, cont=True, screen='start', command=None):
        """ Run SmurfFinder program """
        glob_msg = '(enter "commands" to view valid inputs)'
        while cont==True:

            if screen=='start':
                valid = {'new': "Create new database",
                        'existing': "Use existing database",
                        'commands': "Print valid commands",
                        'exit': "Close program"}
                command = input("Use existing database or create new " + glob_msg + "? ")
                if command=='new':
                    dbname = input("New database name: ")
                    try:
                        self.dbupdate(dbname).create_db()
                        self.dbname = dbname
                        screen = 'summ_select'
                    except OperationalError:
                        print(f"Database {dbname} already exists.")
                elif command=='existing':
                    self.dbname = 'master'
                    screen = 'summ_select'
                elif command=='exit':
                    cont = False
                elif command=='commands':
                    for k,v in valid.items():
                        print(k + ": " + v)
                else:
                    print('Invalid input ' + glob_msg + ".")

            elif screen=='summ_select':
                valid = {'[summoner name]': "Input summoner name to get data.",
                        'commands': "Print valid commands",
                        'exit': "Close program"}
                command = input("What summoner would you like to examine " + glob_msg + "? ")
                if command=='exit':
                    cont = False
                elif command=='commands':
                    for k,v in valid.items():
                        print(k + ": " + v)
                else:
                    self.summoner = command
                    info = self.dbquery(self.dbname).acct_from_db(self.summoner)
                    if info==1:
                        plinfo = self.riotdata().summ_info(self.summoner)
                        self.dbupdate(self.dbname).update_accounts(plinfo)
                        start = input("Start date (YYYY/MM/DD): ")
                        self.start = dt.datetime.strptime(start, '%Y/%m/%d')
                        end = input("End date (YYYY/MM/DD): ")
                        self.end = dt.datetime.strptime(end, '%Y/%m/%d')
                        gamerows, plrows, allpls = self.riotdata().match_in_range(
                            self.summoner, self.start, self.end)
                        self.dbupdate(self.dbname).update_matches(gamerows)
                        self.dbupdate(self.dbname).update_players(plrows)
                        screen = 'summ_info'
                    else:
                        screen = 'summ_info'

            elif screen=='summ_info':
                valid = {'view': "View cached data on user.",
                        'update': "Update user with data from range.",
                        'new': "Select new summoner to get/view data.",
                        'commands': "Print valid commands",
                        'exit': "Close program."}
                command = input(f"""Summoner {self.summoner} selected. View data, update database, or select a new summoner """ + glob_msg + ". ")
                if command=='view':
                    start = input("Start date (YYYY/MM/DD): ")
                    self.start = dt.datetime.strptime(start, '%Y/%m/%d')
                    end = input("End date (YYYY/MM/DD): ")
                    self.end = dt.datetime.strptime(end, '%Y/%m/%d')
                    topplw = self.dbquery(self.dbname).plw_in_range(self.summoner,
                                self.start, self.end)
                    newplw = []
                    for pl in topplw:
                        if pl[0]=='UNKNOWN PLAYER':
                            name = self.riotdata().acct_info(int(pl[1]))
                            if name==1:
                                newplw.append((pl[0], pl[2]))
                            else:
                                newplw.append((name[1], pl[2]))
                                self.dbupdate(self.dbname).update_accounts(name, player='No')
                        else:
                            newplw.append((pl[0], pl[2]))
                    gamesdf = self.dbquery(self.dbname).matches_in_range(self.summoner,
                                self.start, self.end)
                    self.viewdata().plw(newplw)
                    self.viewdata().matchagg(self.summoner, gamesdf)
                elif command=='update':
                    info = self.dbquery(self.dbname).acct_from_db(self.summoner)
                    if info[1]=='None':
                        plinfo = self.riotdata().summ_info(self.summoner)
                        self.dbupdate(self.dbname).update_accounts(plinfo)
                    while True:
                        start = input("Start date (YYYY/MM/DD): ")
                        try:
                            self.start = dt.datetime.strptime(start, '%Y/%m/%d')
                            break
                        except ValueError:
                            print("Invalid input!")
                            continue
                    while True:
                        end = input("End date (YYYY/MM/DD): ")
                        try:
                            self.end = dt.datetime.strptime(end, '%Y/%m/%d')
                            break
                        except ValueError:
                            print("Invalid input!")
                            continue
                    acctID = self.dbquery(self.dbname).acct_from_db(self.summoner)[0]
                    #self.dbupdate(self.dbname).update_updates(acctID, self.start, self.end)
                    cached = self.dbquery(self.dbname).gameids(acctID)
                    gamerows, plrows, allpls = self.riotdata().match_in_range(
                        self.summoner, self.start, self.end, cached=cached)
                    self.dbupdate(self.dbname).update_matches(gamerows)
                    self.dbupdate(self.dbname).update_players(plrows)
                    screen = 'summ_info'
                elif command=='new':
                    screen = 'summ_select'
                elif command=='exit':
                    cont = False
                elif command=='commands':
                    for k,v in valid.items():
                        print(k + ": " + v)
                else:
                    print('Invalid input ' + glob_msg + ".")
            else:
                print("How'd you do that?")

        print("Thank you for using SmurfFinder!")
