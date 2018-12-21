from riotwatcher import RiotWatcher
from .data.base import api_key, reg, today
from requests import HTTPError
import datetime as dt
from math import ceil

class Riotdata(object):
    """ Get fresh data from Riot API. """
    def __init__(self):
        self.api_key = api_key
        self.reg = reg
        self.today = today
        self.watcher = RiotWatcher(api_key)

    def summ_info(self, summ):
        """ Get summoner info from API and format for database. """
        while True:
            try:
                summdto = self.watcher.summoner.by_name(self.reg, summ)
            except HTTPError as err:
                if err.response.status_code == 429:
                    print('Too many requests, waiting 30 seconds...')
                    time.sleep(15)
                    continue
                elif err.response.status_code == 404:
                    return 1
                elif err.response.status_code == 503:
                    print('Server delay, retrying...')
                    continue
                else:
                    raise
            break
        return [summdto['accountId'], summ, None, self.today]

    def match_in_range(self, summ, start, end, cached=None):
        """ Get matches in given date range from API and format for database. """
        try:
            acctID = self.summ_info(summ)[0]
        except TypeError:
            return 1

        def epochtodate(ms):
            ymdhms = dt.datetime.fromtimestamp(ms/1000).strftime('%Y%m%d %H:%M:%S')
            return ymdhms

        stime = int((start-dt.datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        etime = int((end - dt.datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        iters = ceil((etime - stime) / 604800000) # ms in wk
        diffs = int(round((etime - stime) / iters))
        # initialize return lists
        gamerows = []
        plrows = []

        for i in range(1, iters + 1):
            while True:
                try:
                    stime += (diffs*(i-1))
                    matches = self.watcher.match.matchlist_by_account(self.reg,acctID,
                        queue=420,begin_time=stime,end_time=stime+diffs)
                    gameIDs = [match['gameId'] for match in matches['matches']]
                except HTTPError as err:
                    if err.response.status_code == 429:
                        print('Too many requests, waiting 30 seconds...')
                        time.sleep(30)
                        continue
                    elif err.response.status_code == 404:
                        raise
                    elif err.response.status_code == 503:
                        print('Server delay, retrying...')
                        continue
                    else:
                        raise
                break

            if cached is not None:
                gameIDs = [id for id in gameIDs if id not in cached]

            print(f"{len(gameIDs)} new games found for segment {i} of {iters}")

            if len(gameIDs) > 0:
                for game in gameIDs:
                    print(f"Getting data for game {game}...")
                    while True:
                        try:
                            match = watcher.match.by_id(self.reg,game)
                        except HTTPError as err:
                            if err.response.status_code == 429:
                                print('Too many requests, waiting 30 seconds...')
                                time.sleep(30)
                                continue
                            elif err.response.status_code == 404:
                                print(f'No results for game {game}. Major error.')
                                break
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

        return gamerows, plrows
