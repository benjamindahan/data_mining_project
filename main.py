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
# Some players get cut by their team: they have a salary but they are not in the team roster
players_cut = []
fields_players_stats = ts.get_player_stats_fields(c.URL_FIELDS_PLAYER_STATS)

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
----------------------------------------------SQL TABLES' COLUMNS----------------------------------------------
"""
cols_players = db.get_table_columns_label(cursor, 'players')
cols_rosters = db.get_table_columns_label(cursor, 'rosters')
cols_salaries = db.get_table_columns_label(cursor, 'salaries')
cols_teams_summaries = db.get_table_columns_label(cursor, 'teams_summaries')
cols_teams_stats = db.get_table_columns_label(cursor, 'teams_stats')
cols_teams_ranks = db.get_table_columns_label(cursor, 'teams_ranks')
cols_players_stats = db.get_table_columns_label(cursor, 'players_stats')
cols_games = db.get_table_columns_label(cursor, 'games')
cols_boxscores = db.get_table_columns_label(cursor, 'boxscores')

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
        team_id = db.get_id('team', cursor, team)
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
        cols_rosters = db.get_table_columns_label(cursor, 'rosters')

        for player in ts.get_roster(soup, season):
            if player[2] in players_cut:
                query = db.update_players_cut(player)
                cursor.execute(query)
                connection.commit()
                players_cut.remove(player[2])

            elif player[2] not in db.x_fetchall(cursor, "SELECT DISTINCT(player_name) FROM players;"):
                query = db.create_insert_query('players', cols_players)
                values = [data for index, data in enumerate(player) if index in c.INDEXES_PLAYERS]
                cursor.execute(query, values)
                connection.commit()


            """
            ----------------------------------------------ROSTERS----------------------------------------------
            """
            player_id = db.get_id('player', cursor, player[2])
            query = db.create_insert_query('rosters', cols_rosters)
            values = [data for index, data in enumerate(player) if index in c.INDEXES_ROSTERS] + [player_id] + [team_id]
            cursor.execute(query, values)
            connection.commit()

        """
        ----------------------------------------------SALARIES----------------------------------------------
        """
        for player, salary in ts.get_salaries(page_html):
            print(player)
            try:
                player_id = db.get_id('player', cursor, player)
            except TypeError:
                # explain
                players_cut.append(player)
                query_player = db.create_insert_query('players', ['player_name'])
                values_player = [player]
                cursor.execute(query_player, values_player)
                connection.commit()
                player_id = db.get_id('player', cursor, player)
            query = db.create_insert_query('salaries', cols_salaries)
            values = [season, salary, player_id, team_id]
            cursor.execute(query, values)
            connection.commit()

        """
        ----------------------------------------------TEAM SUMMARY----------------------------------------------
        """
        query = db.create_insert_query('teams_summaries', cols_teams_summaries)
        values = [season] + ts.get_team_summary(soup) + [team_id]
        cursor.execute(query, values)
        connection.commit()

        """
        ----------------------------------------------PLAYER STATS----------------------------------------------
        """
        nr_of_players = db.get_nr_players(cursor, team_id, season)
        query = db.create_insert_query('players_stats', cols_players_stats)
        for player in ts.get_player_stats(soup, nr_of_players, fields_players_stats):
            print(player)
            if player[0] not in c.PLAYERS_NAMES:
                player_id = db.get_id('player', cursor, player[0])
                values = [season] + list(player[1:]) + [player_id] + [team_id]
                values = [None if value == "" else value for value in values]
                print(values)
                cursor.execute(query, values)
                connection.commit()






