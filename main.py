import sys
import pymysql
import grequests
import src.conf as c
import src.scraping_team_season as ts
import src.scraping_boxscores as bs
import src.database_insertion as db
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import argparse

assert load_dotenv() is True
pswd = os.getenv("password")

"""
----------------------------------------------INITIAL VARIABLES----------------------------------------------
"""
# Getting all the seasons and teams
seasons = [str(year) for year in range(c.FIRST_SEASON, c.LAST_SEASON)]
teams = ts.get_teams()
# Some players get cut by their team: they have a salary but they are not in the team roster
players_cut = []
fields_players_stats = ts.get_player_stats_fields(c.URL_FIELDS_PLAYER_STATS)

"""
---------------------------------------------COMMAND LINE ARGUMENTS---------------------------------------------
"""
# Creating the command line arguments
parser = argparse.ArgumentParser(description='Get data about NBA teams/seasons')
parser.add_argument('data_type', nargs=1, choices=['summaries', 'rosters', 'players_stats', 'teams_stats',
                                                   'teams_ranks', 'salaries', 'all'],
                    help='The type of data you want to scrape')
parser.add_argument('-boxscores', action='store_true',
                    help='Choose to scrape boxscores. ⚠️ Be careful! It takes a long time')
parser.add_argument('-t', nargs='*', default='all',
                    help=f"""The teams you want to get data from. Choose between these teams: 
                        {teams}. By default, all the teams are used.
                        Example: -t MIA LAL""")
parser.add_argument('-s', nargs='*', default='all',
                    help='The seasons you want to get data from. Choose seasons between 2008 and 2021.'
                         'By default, all the seasons are used.'
                         'Example: -s 2010 2015')

args = parser.parse_args()

print("Let's create the best basketball database ever! 🏀⛹🏾⛹🏽‍")

# We get the team names that were requested by the user
if args.t != 'all':
    try:
        assert set(args.t).issubset(teams)
    except AssertionError:
        print("Oops!  That was not a valid team. Try again...")
        print(f"Here are the possible values: {teams}")
        sys.exit()
    finally:
        teams = args.t

# We get all the seasons requested by the user
if args.s != 'all':
    try:
        assert set(args.s).issubset(seasons)
    except AssertionError:
        print("Oops!  That was not a valid season. Try again...")
        print(f"Here are the possible values: {seasons}")
        sys.exit()
    finally:
        seasons = args.s

"""
----------------------------------------------CONNECTION/CURSOR----------------------------------------------
"""
# We create the connection with SQL and the cursor.
try:
    connection, cursor = db.create_sql_connection(pswd)
    query = 'USE basketball_reference;'
    cursor.execute(query)
except pymysql.err.OperationalError:
    print("☠️ You haven't created the basketball_reference database! Shame on you! 🏀")
    sys.exit()

"""
----------------------------------------------TEAMS----------------------------------------------
"""
# We scrape and create the team tables of SQL
query = "INSERT IGNORE INTO teams (team_name) VALUES (%s);"

for team in teams + c.OLD_TEAMS_LABELS:
    cursor.execute(query, team)
    connection.commit()

"""
----------------------------------------------SQL TABLES' COLUMNS----------------------------------------------
"""
# We get all the columns of all the tables in SQL that will be used later
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
----------------------------------------------URLS/REQUESTS FOR TEAMS/SEASONS------------------------------------------
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
        # We create the table players where all the player information is stored
        cols_players = db.get_table_columns_label(cursor, 'players')
        cols_rosters = db.get_table_columns_label(cursor, 'rosters')

        # We make sure all the players have the accurate name
        for player in ts.get_roster(soup, season):
            player[2] = ts.strip_players_suffixes(player[2])
            player[2] = ts.get_real_name(player[2])

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
            # We scrape and create the rosters table
            if args.data_type[0] in ['rosters', 'all']:
                player_id = db.get_id('player', cursor, player[2])
                query = db.create_insert_query('rosters', cols_rosters)
                values = [data for index, data in enumerate(player) if index in c.INDEXES_ROSTERS] + [player_id] + [
                    team_id]
                cursor.execute(query, values)
                connection.commit()

        """
        ----------------------------------------------SALARIES----------------------------------------------
        """
        # We scrape and create the salaries table
        if args.data_type[0] in ['salaries', 'all']:
            for player, salary in ts.get_salaries(page_html):
                player = ts.strip_players_suffixes(player)
                player = ts.get_real_name(player)
                # Sometimes a player appears in salaries but not in the rosters, we fix this by focusing on players_cut
                try:
                    player_id = db.get_id('player', cursor, player)
                except TypeError:
                    # Some players are cut by their team (team A) and hired by another team (team B)
                    # That means that the player still appears in team A salaries but not in the roster
                    # For these reasons, we need to deal with the players_cut list
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
        # We scrape and create the team summary table
        if args.data_type[0] in ['summaries', 'all']:
            query = db.create_insert_query('teams_summaries', cols_teams_summaries)
            values = [season] + ts.get_team_summary(soup) + [team_id]
            cursor.execute(query, values)
            connection.commit()

        """
        ----------------------------------------------PLAYER STATS----------------------------------------------
        """
        # We scrape and create the players stats
        if args.data_type[0] in ['players_stats', 'all']:
            query = db.create_insert_query('players_stats', cols_players_stats)
            for player in ts.get_player_stats(soup, fields_players_stats):
                player = list(player)
                player[0] = ts.strip_players_suffixes(player[0])
                player[0] = ts.get_real_name(player[0])

                player_id = db.get_id('player', cursor, player[0])

                values = [season] + player[1:] + [player_id] + [team_id]

                values = [None if value == "" else value for value in values]
                cursor.execute(query, values)
                connection.commit()

        """
        ----------------------------------------------TEAMS STATS----------------------------------------------
        """
        # We scrape and create the teams stats
        if args.data_type[0] in ['teams_stats', 'all']:
            query = db.create_insert_query('teams_stats', cols_teams_stats)
            for team_stats in ts.get_team_opponent_stats(page_html):
                values = [season] + team_stats + [team_id]
                cursor.execute(query, values)
                connection.commit()

        """
        ----------------------------------------------TEAMS RANKS----------------------------------------------
        """
        # We scrape and create the teams ranks
        if args.data_type[0] in ['teams_ranks', 'all']:
            query = db.create_insert_query('teams_ranks', cols_teams_ranks)
            for team_ranks in ts.get_team_opponent_ranks(page_html):
                values = [season] + team_ranks + [team_id]
                cursor.execute(query, values)
                connection.commit()

"""
----------------------------------------------GAMES------------------------------------------
"""
# We scrape and create the games table
if args.boxscores:
    query_games = db.create_insert_query('games', cols_games)
    for season in seasons:
        # We define all the lists that will be updated
        month = []
        day = []
        year = []
        box_score = []
        visitor_team = []
        home_team = []
        data_for_query = []

        # Creating the list of urls
        list_of_urls_scores = bs.url_creation(season)

        # Making the requests with GRequests
        responses = bs.get_request(list_of_urls_scores)

        for url, response in zip(list_of_urls_scores, responses):
            if response is not None:
                # Creating the soup object
                soup = BeautifulSoup(response.text, "html.parser")

                # Scraping all the data that will be stored as URLS
                box_score_aux, home, visitor, date = bs.scraping_urls(soup, box_score)

                # Cleaning the URLS
                bs.cleaning_urls(box_score_aux, home, visitor, date, home_team, visitor_team, day, month, year)
                data_for_query = bs.doubling_lists(day, month, year, home_team, visitor_team, box_score)
                teams_ids = [db.get_id('team', cursor, team) for team in data_for_query[3]]
                visitors_ids = [db.get_id('team', cursor, visitor) for visitor in data_for_query[4]]

                del data_for_query[3:5]
                data_for_query += [teams_ids, visitors_ids]

        for values in zip(*data_for_query):
            cursor.execute(query_games, values)
            connection.commit()

        """
        ----------------------------------------------BOXSCORES------------------------------------------
        """
        # We scrape and create the boxscores table
        # We define all the lists that will be updated
        games_ids = []
        games_urls = []
        games_teams = []

        query_urls = db.get_boxscore_query(season)
        cursor.execute(query_urls)
        games_args = [(db["game_id"], db["url"], db["team_id"]) for db in cursor.fetchall()]
        query_boxscores = db.create_insert_query('boxscores', cols_boxscores)

        # games_ids is a list with all the games ids from the season in the loop
        # games_urls is a list with all the games urls from the season in the loop
        # games_teams is a list with all the teams related to the games
        for row in games_args:
            games_ids.append(row[0])
            games_urls.append(row[1])
            games_teams.append(row[2])

        print('initialize')
        responses_teams_ids = bs.get_data_grequest(games_urls, games_teams, games_ids)
        print('finish grequest')

        # We get the fields (columns names) from basic boxscores (assists, rebounds, points...)
        basic_fields = bs.get_basic_fields(c.URL_FIELDS_BOXSCORE)
        # We get the fields (columns names) from advanced boxscores
        advanced_fields = bs.get_advanced_fields(c.URL_FIELDS_BOXSCORE)

        for response, team_id, game_id in responses_teams_ids:
            # we get the team name based on the team id
            team = db.get_team_from_id(cursor, team_id)
            print(team)
            # we get the basic boxscore table
            basic_table = bs.get_table_basic_boxscore(response, team)
            # we get the advanced boxscore table
            advanced_table = bs.get_table_advanced_boxscore(response, team)

            # we get the names of the players linked to these stats
            players = bs.get_players(basic_table)
            # we clean their names
            players = [ts.get_real_name(ts.strip_players_suffixes(player)) for player in players]
            # we get the id related to this name
            players_id = [db.get_id('player', cursor, player) for player in players]

            # we get, column by column, the data from each field in basic boxscore
            # we link these data to the players ids
            basic_boxscore = bs.get_boxscore(basic_table, basic_fields, players_id)
            # we replace the 'dnp' (did not play) by None to get Null values in the sql table
            basic_boxscore = bs.fill_dnp(basic_boxscore)

            # we get, column by column, the data from each field in advanced boxscore
            # we link these data to the players ids
            advanced_boxscore = bs.get_boxscore(advanced_table, advanced_fields, players_id)
            # we replace the 'dnp' (did not play) by None to get Null values in the sql table
            advanced_boxscore = bs.fill_dnp(advanced_boxscore)

            # we pop last element of basic_boxscore (player name) because it appears in advanced_boxscore as well
            basic_boxscore.pop(-1)
            # we pop first element of advanced_boxscore (minutes) because it appears in basic_boxscore as well
            advanced_boxscore.pop(0)
            # we add create game_id, a list with same length than players_id (hence basic or advanced boxscore)
            # each element of this list is the same value, game_id, foreign key for table games
            game_id = [game_id for _ in range(len(players_id))]

            # boxscore is the final boxscore, with the basic fields, advanced fields and game_id
            boxscore = basic_boxscore + advanced_boxscore + [game_id]

            # finally, we zip boxscore to get its data row by row instead of column by column
            for values in zip(*boxscore):
                # we insert each row in the boxscore sql table
                values = [None if value == "" else value for value in values]
                cursor.execute(query_boxscores, values)
                connection.commit()
