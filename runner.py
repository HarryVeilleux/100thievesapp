from smurf import Smurffinder

smurf = Smurffinder()
smurf.screens()

stuff = """
smurf = Smurffinder()
newdb = 'y'#input("New database? (Y/N) ")
if newdb.lower()=='y':
    dbname = 'first'#input("Database name? ")
    smurf.dbupdate(dbname).create_db()
else:
    dbname = 'master'

summ = 'aphromoo'#input("First summoner: ")
info = smurf.dbquery(dbname).acct_from_db(summ)

if info==1:
    summl = smurf.riotdata().summ_info(summ)
    smurf.dbupdate(dbname).update_accounts(summl)
    info = smurf.dbquery(dbname).acct_from_db(summ)

smurf.viewdata().summ(info)
"""
