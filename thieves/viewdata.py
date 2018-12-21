import pandas as pd

class Viewdata(object):
    """ Pretty print data from database. """
    def __init__(self):
        pass

    def summ(self, row):
        """ Print summoner information. """
        head = ['AccountID', 'Summoner', 'Player', 'Last Updated']
        for el in head:
            print(el, end='\t')
        print('')
        for el in row:
            if el is None:
                print('UNKNOWN', end='\t')
            else:
                print(el, end='\t')
        print('')

    def plw(self, topplw):
        """ Print top 10 summoners played with. """
        for pl in topplw:
            print(pl[0] + ' - ' + str(pl[1]))

    def matchagg(self, summ, gamesdf):
        """ Print aggregated match data. """
        head = ['Name', 'Games', 'Wins', 'Kills', 'Deaths', 'Assists']
        aggdata = [summ, gamesdf['Key'].count(), sum(gamesdf['Win']),
            sum(gamesdf['Kills']), sum(gamesdf['Deaths']), sum(gamesdf['Assists'])]
        for el in head:
            print(head, end='\t')
        print('')
        for point in aggdata:
            print(str(point), end='\t')
        print('')
