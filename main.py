import grequests
import conf as c
import scraping_team_season as ts
import database_insertion as db
import re
from bs4 import BeautifulSoup
import pymysql
from dotenv import load_dotenv
import os

assert load_dotenv() == True
pswd = os.getenv("password")


"""
----------------------------------------------INITIAL VARIABLES----------------------------------------------
"""

seasons = [str(year) for year in range(c.FIRST_SEASON, c.LAST_SEASON)]
teams = ts.get_teams()




"""
----------------------------------------------CONNECTION/CURSOR----------------------------------------------
"""

connection, cursor = db.create_sql_connection(pswd)
query = 'USE basketball_reference;'
cursor.execute(query)


"""
----------------------------------------------TEAMS----------------------------------------------
"""



query = "INSERT INTO teams (team_name) VALUES (%s);"

for team in teams + c.OLD_TEAMS_LABELS:
    cursor.execute(query, team)
    connection.commit()


"""
----------------------------------------------URLS/REQUESTS----------------------------------------------
"""

# We create a list with all the URLS we need to scrape (TEAM and SEASON are changing)
list_of_urls = []
for season in seasons:
    for team in teams:
        if team in c.OLD_TEAMS and int(season) <= int(c.OLD_TEAMS[team]['until_season']):
            team = c.OLD_TEAMS[team]['old_name']
        list_of_urls.append(c.URL_1 + team + c.URL_2 + season + c.URL_3)

# Making the requests with GRequests
rs = (grequests.get(url) for url in list_of_urls)
responses = grequests.map(rs, size=c.BATCHES)

# For each url we call the functions in order to get the information desired.
for url, response in zip(list_of_urls, responses):
    if response is not None:
        # Extracting the team and the season from the urls to be able to pass it as a parameter to the functions.
        team = re.findall(f"{c.URL_1}(.*){c.URL_2}", url)[0]
        pattern_for_season = team + "\/"
        season = re.findall(f"{pattern_for_season}(.*){c.URL_3}", url)[0]

        # Prints that help us debug
        print("TEAM: ", team)
        print("SEASON: ", season)

        # Creating the soup object
        soup = BeautifulSoup(response.text, "html.parser")
        page_html = str(soup.find())


        """
        ----------------------------------------------PLAYERS----------------------------------------------
        """
        cols_players = db.get_table_columns_label(cursor, 'players')

        for player in ts.get_roster(soup, team, season):
            if player[3] not in db.x_fetchall(cursor, "SELECT DISTINCT(player_name) FROM players;"):
                query = db.create_insert_query('players', cols_players)
                values = [data for index, data in enumerate(player) if index in c.INDEXES_PLAYERS]
                cursor.execute(query, values)
                connection.commit()


            """
            ----------------------------------------------ROSTERS----------------------------------------------
            """
            player_id = [db.get_id('player', cursor, player[3])]
            team_id = [db.get_id('team', cursor, player[0])]
            cols_rosters = db.get_table_columns_label(cursor, 'rosters')
            query = db.create_insert_query('rosters', cols_rosters)
            values = [data for index, data in enumerate(player) if index in c.INDEXES_ROSTERS] + player_id + team_id
            cursor.execute(query, values)
            connection.commit()
            print(cols_rosters)