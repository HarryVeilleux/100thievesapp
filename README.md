# 100thievesapp
SmurfFinder for 100T application

Python script to pull match and summoner data from Riot's API and interpret it in order to identify professional NA LCS player accounts

1. Start script at command line by running "runner.py"

2. Enter your API key (this step not required if you have edited 'thieves/data/base.py' to include your current API key).

3. Choose a summoner to start from (HIGHLY RECOMMEND CHOOSING A SUMMONER FOR WHICH YOU ALREADY KNOW THE PLAYER, i.e. 'aphromoo' = 'Aphromoo')

4. Program will prompt you to view cached data from master.db, update summoner with data from Riot's API (you will choose the date range after entering 'update' command), or choose a new summoner.

5. All update commands will break the date range into chunks smaller than 1 week (Riot's request limit) and iterate over them; ranges > 1 month can take several minutes to complete because of rate limiting.

6. New data is automatically added to 'thieves/data/master.db' file, which is queried with 'view' commands.

7. Use 'new' command to choose a new summoner (HIGHLY RECOMMEND CHOOSING A SUMMONER FROM TOP 10 PLAYED WITH).

8. Program will loop to the new summoner.
