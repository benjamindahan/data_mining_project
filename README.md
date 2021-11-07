# ITC - Data Mining Project
## Scraping Basket Ball Reference website
![Image](https://www.basketballnetwork.net/app/uploads/2021/03/Michael-Jordan-The-Last-Shot-min.jpeg)
In this project we have scraped the NBA [Basketball Reference](https://www.basketball-reference.com/teams/) website.

### Introduction
The NBA (National Basketball Association) is the most popular basketball league in the world. 
It is composed of 30 teams, divided in two conferences: the Western Conference and the Eastern Conferece.
Basketball reference is a website that gathers all the information regarding the NBA: player statistics, salaries, results, team statistics, boxscores...

### Our project
In this project, for each one of the 30 teams and for each season between (2008-2021), we scraped from basketball reference the following information
1. The season `summary` of the team: final rank of the regular season, coach, playoffs results and offesinve and deffensive ratings, among others. 
2. The season `roster` of the team, listing all the players in the roster and their characteristics (height, weight, nationality, full name...)
3. The individual `statistics of the players` such as points per game, rebounds per game, steals per game, assists per game...
4. The `salary` of each player 
5. The `team and opponent statistics` that compares the statistics of each with all the competence.
6. The `team and opponent rank` that is analogue to nr 5 but with the rank.

### Contents of the repository
- `web_scraping.py` where all the data scraping takes place
- `rosters.csv` , `salaries.json`, `statistics.json`, `summary.csv`, `team_opponent_rank.csv`, `team_opponent_stats.csv` with all the data collected from the web scraping


### Tools
- [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [json](https://docs.python.org/3/library/json.html)
- [csv](https://docs.python.org/3/library/csv.html)
> Authors: Benjamin Dahan and Julieta Staryfurman 