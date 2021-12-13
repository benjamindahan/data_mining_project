import sys
import grequests
import src.conf as c
import src.scraping_team_season as ts
import src.scraping_boxscores as bs
import src.database_insertion as db
import src.api as api
import database.database_creation as dbc
import re
from bs4 import BeautifulSoup
import argparse
import logging


def get_command_line_arguments(teams):
    """
    This function defines and parses arguments given by the user on the command line
    :param teams: the possible teams
    :return: the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Get data about NBA teams/seasons')
    parser.add_argument('data_type', nargs=1, choices=['summaries', 'rosters', 'players_stats', 'teams_stats',
                                                       'teams_ranks', 'salaries', 'standings', 'all'],
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

    logging.info("✅Starting the program!!")
    print("Let's create the best basketball database ever! 🏀⛹🏾⛹🏽‍")

    return args


def verify_teams_integrity(args, teams):
    """
    This functions checks the integrity of the parsed arguments and returns selected teams
    if they pass the asserts
    :param args: the parsed args of the command line
    :param teams: the possible teams
    :return: the selected teams
    """
    if args.t != 'all':
        try:
            assert set(args.t).issubset(teams)
            logging.info("✅Correct values for the teams")
        except AssertionError:
            print("Oops!  That was not a valid team. Try again...")
            print(f"Here are the possible values: {teams}")
            logging.critical("❌Introduced team not valid")
            sys.exit()
        finally:
            teams = args.t
    return teams


def verify_seasons_integrity(args, seasons):
    """
    This functions checks the integrity of the parsed arguments and returns selected seasons
    if they pass the asserts
    :param args: the parsed args of the command line
    :param seasons: the possible seasons
    :return: the selected seasons
    """
    if args.s != 'all':
        try:
            assert set(args.s).issubset(seasons)
            logging.info("✅Correct values for the seasons")
        except AssertionError:
            print("Oops!  That was not a valid season. Try again...")
            print(f"Here are the possible values: {seasons}")
            logging.critical("❌Introduced season not valid")
            sys.exit()
        finally:
            seasons = args.s
    return seasons


def create_and_use_database(pswd):
    """
    This function creates the database basketball_reference, create the connection/cursor and starts using the database
    :param pswd: mysql password
    :return: sql connection and cursor
    """
    dbc.creation_script()
    logging.info("✅Database created!!")
    connection, cursor = db.create_sql_connection(pswd)
    logging.info("✅Connection created!!")
    query = 'USE basketball_reference;'
    cursor.execute(query)
    return connection, cursor


def api_insert_teams(connection, cursor, teams):
    """
    This function requests the api to get teams info and insert these in the teams table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param teams: the selected teams
    """
    # We get all the columns of the teams table
    cols_teams = db.get_table_columns_label(cursor, 'teams')

    # We scrape and create the teams table of SQL
    all_values = api.get_teams_values(teams)
    for values in all_values:
        query = db.create_insert_query('teams', cols_teams)
        cursor.execute(query, values)
        connection.commit()

    query = "INSERT IGNORE INTO teams (team_name) VALUES (%s);"
    for team in c.OLD_TEAMS_LABELS:
        cursor.execute(query, team)
        connection.commit()
    logging.info("✅Table teams completed!!")


def api_insert_standings(args, connection, cursor):
    """
    This function requests the api to get standings info and insert these in the standings table
    :param args: the parsed args of the command line
    :param connection: the sql connection
    :param cursor: the sql cursor
    """
    # We scrape and create the standings table of SQL only if requested by the user in args
    if args.data_type[0] in ['standings', 'all']:
        # We get all the columns of the standings table
        cols_standings = db.get_table_columns_label(cursor, 'standings')
        teams_dictionaries = db.get_teams_dictionary(cursor)
        all_standing_values = api.get_standings(teams_dictionaries)
        for values in all_standing_values:
            query = db.create_insert_query('standings', cols_standings)
            cursor.execute(query, values)
            connection.commit()
        logging.info("✅Table standings completed!!")


def get_urls_and_responses(seasons, teams):
    """
    This function creates a list of urls that we want to scrape and request each of these urls to get responses
    :param seasons: the parsed seasons
    :param teams: the parsed teams
    :return: the list of urls to scrape and the responses from these urls
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

    return list_of_urls, responses


def extract_info_response(response, cursor, url):
    """
    Based on a response from a requested URL, this function returns the team_id, the season, the soup and the html
    of the url
    :param response: the response from the requested url
    :param cursor: the sql cursor
    :param url: the requested url
    :return: the team_id, the season, the soup and the html of the requested url
    """
    # Extracting the team and the season from the urls to be able to pass it as a parameter to the functions.
    team = re.findall(f"{c.URL_1}(.*){c.URL_2}", url)[0]
    team_id = db.get_id('team', cursor, team)
    pattern_for_season = team + "\/"
    season = re.findall(f"{pattern_for_season}(.*){c.URL_3}", url)[0]

    # Prints that help us debug
    logging.info(f"✅Scraping Team: {team}")
    logging.info(f"✅Scraping Season: {season}")
    print(team, season)

    # Creating the soup object
    soup = BeautifulSoup(response.text, "html.parser")
    page_html = str(soup.find())

    return team_id, season, soup, page_html


def scrape_insert_player(connection, cursor, player, players_cut):
    """
    Get a scraped player, check his name integrity and insert him to the players table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param player: the scraped player
    :param players_cut: the list of players cut by their team
    """
    player[2] = ts.strip_players_suffixes(player[2])
    player[2] = ts.get_real_name(player[2])

    if player[2] in players_cut:
        query = db.update_players_cut(player)
        cursor.execute(query)
        connection.commit()
        players_cut.remove(player[2])

    elif player[2] not in db.x_fetchall(cursor, "SELECT DISTINCT(player_name) FROM players;"):
        cols_players = db.get_table_columns_label(cursor, 'players')
        query = db.create_insert_query('players', cols_players)
        values = [data for index, data in enumerate(player) if index in c.INDEXES_PLAYERS]
        cursor.execute(query, values)
        connection.commit()


def scrape_insert_roster(connection, cursor, args, player, team_id):
    """
    Get scraped roster and add it to the rosters table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param args: the parsed args from the command line
    :param player: the scraped player
    :param team_id: the id of the team
    """
    if args.data_type[0] in ['rosters', 'all']:
        player_id = db.get_id('player', cursor, player[2])
        cols_rosters = db.get_table_columns_label(cursor, 'rosters')
        query = db.create_insert_query('rosters', cols_rosters)
        values = [data for index, data in enumerate(player) if index in c.INDEXES_ROSTERS] + [player_id] + [
            team_id]
        cursor.execute(query, values)
        connection.commit()


def scrape_insert_salaries(connection, cursor, args, players_cut, page_html, season, team_id):
    """
    Get scraped salaries and add them to the salaries table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param args: the parsed args from the command line
    :param players_cut: the list of players cut by their team
    :param page_html: the html of the scrapped page
    :param season: the year of the nba season
    :param team_id: the id of the team
    """
    # We scrape and create the salaries table
    if args.data_type[0] in ['salaries', 'all']:
        for player, salary in ts.get_salaries(page_html):
            player = ts.strip_players_suffixes(player)
            player = ts.get_real_name(player)
            # Sometimes a player appears in salaries but not in the rosters
            # we fix this by focusing on players_cut
            try:
                player_id = db.get_id('player', cursor, player)
            except TypeError:
                logging.error(f"❌This player ({player}) was cut by their team and hired by another one !!")
                # Some players are cut by their team (team A) and hired by another team (team B)
                # That means that the player still appears in team A salaries but not in the roster
                # For these reasons, we need to deal with the players_cut list
                players_cut.append(player)
                query_player = db.create_insert_query('players', ['player_name'])
                values_player = [player]
                cursor.execute(query_player, values_player)
                connection.commit()
                player_id = db.get_id('player', cursor, player)
            cols_salaries = db.get_table_columns_label(cursor, 'salaries')
            query = db.create_insert_query('salaries', cols_salaries)
            values = [season, salary, player_id, team_id]
            cursor.execute(query, values)
            connection.commit()
    logging.info("✅Table salaries completed!!")


def scrape_insert_team_summary(connection, cursor, args, soup, season, team_id):
    """
    Get scraped team summary and add it to the summaries table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param args: the parsed args from the command line
    :param soup: the soup object
    :param season: the season year
    :param team_id: the id of the team
    """
    if args.data_type[0] in ['summaries', 'all']:
        cols_teams_summaries = db.get_table_columns_label(cursor, 'teams_summaries')
        query = db.create_insert_query('teams_summaries', cols_teams_summaries)
        values = [season] + ts.get_team_summary(soup) + [team_id]
        cursor.execute(query, values)
        connection.commit()
    logging.info("✅Table team summaries completed!!")


def scrape_insert_players_stats(connection, cursor, args, season, team_id, soup):
    """
    Get scraped players stats and add them to the players_stats table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param args: the parsed args from the command line
    :param season: the year of the nba season
    :param team_id: the id of the team
    :param soup: the soup object of the scrapped page
    """
    # We scrape and create the players stats
    if args.data_type[0] in ['players_stats', 'all']:
        cols_players_stats = db.get_table_columns_label(cursor, 'players_stats')
        query = db.create_insert_query('players_stats', cols_players_stats)
        fields_players_stats = ts.get_player_stats_fields(c.URL_FIELDS_PLAYER_STATS)
        for player in ts.get_player_stats(soup, fields_players_stats):
            player = list(player)
            player[0] = ts.strip_players_suffixes(player[0])
            player[0] = ts.get_real_name(player[0])

            player_id = db.get_id('player', cursor, player[0])

            values = [season] + player[1:] + [player_id] + [team_id]

            values = [None if value == "" else value for value in values]
            cursor.execute(query, values)
            connection.commit()
    logging.info("✅Table player statistics completed!!")


def scrape_insert_teams_stats_ranks(connection, cursor, args, season, team_id, page_html):
    """
    Get scraped teams stats and ranks and add them to the tables teams_stats and teams_ranks
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param args: the parsed args from the command line
    :param season: the year of the nba season
    :param team_id: the id of the team
    :param page_html: the html of the scrapped page
    """
    # We scrape and create the teams stats
    if args.data_type[0] in ['teams_stats', 'all']:
        cols_teams_stats = db.get_table_columns_label(cursor, 'teams_stats')
        query = db.create_insert_query('teams_stats', cols_teams_stats)
        for team_stats in ts.get_team_opponent_stats(page_html):
            values = [season] + team_stats + [team_id]
            cursor.execute(query, values)
            connection.commit()
    logging.info("✅Table teams statistics completed!!")

    # We scrape and create the teams ranks
    if args.data_type[0] in ['teams_ranks', 'all']:
        cols_teams_ranks = db.get_table_columns_label(cursor, 'teams_ranks')
        query = db.create_insert_query('teams_ranks', cols_teams_ranks)
        for team_ranks in ts.get_team_opponent_ranks(page_html):
            values = [season] + team_ranks + [team_id]
            cursor.execute(query, values)
            connection.commit()
    logging.info("✅Table teams ranks completed!!")


def scrape_insert_games(connection, cursor, query_games, season):
    """
    Scrape games info and add them to the games table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param query_games: sql query to insert new rows to the table games
    :param season: the year of the nba season
    """
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

    logging.info(f"✅Table games completed for year {season}!!")


def prepare_boxscores_scraping(cursor, season):
    """This function prepares the scraping of the boxscores by returning important objects that will be used throughout
    the process
    :param cursor: the sql cursor
    :param season: the year if the nba season
    :return: responses_teams_ids: zip containing responses and linked team_ids and game_ids,
            basic_fields: fields (columns names) from basic boxscores
            advanced_fields: fields (columns names) from advanced boxscores
            query_boxscores: sql query to insert new rows to the table boxscore
    """
    # We scrape and create the boxscores table
    # We define all the lists that will be updated
    games_ids = []
    games_urls = []
    games_teams = []

    query_urls = db.get_boxscore_query(season)
    cursor.execute(query_urls)
    games_args = [(db_["game_id"], db_["url"], db_["team_id"]) for db_ in cursor.fetchall()]

    # games_ids is a list with all the games ids from the season in the loop
    # games_urls is a list with all the games urls from the season in the loop
    # games_teams is a list with all the teams related to the games
    for row in games_args:
        games_ids.append(row[0])
        games_urls.append(row[1])
        games_teams.append(row[2])

    print('initialize')
    logging.info(f"✅Initializing Grequests for season: {season}!!")
    responses_teams_ids = bs.get_data_grequest(games_urls, games_teams, games_ids)
    print('finish grequest')
    logging.info(f"✅Finishing Grequests for season: {season}!!")

    # We get the fields (columns names) from basic boxscores (assists, rebounds, points...)
    basic_fields = bs.get_basic_fields(c.URL_FIELDS_BOXSCORE)
    # We get the fields (columns names) from advanced boxscores
    advanced_fields = bs.get_advanced_fields(c.URL_FIELDS_BOXSCORE)

    # We get the sql query to insert new rows to the table boxscore
    cols_boxscores = db.get_table_columns_label(cursor, 'boxscores')
    query_boxscores = db.create_insert_query('boxscores', cols_boxscores)

    return responses_teams_ids, basic_fields, advanced_fields, query_boxscores


def scrape_boxscores(cursor, response, team_id, basic_fields, advanced_fields, season):
    """
    Based on the response of a requested game url, this function returns the basic and advanced boxscores
    :param cursor: the sql cursor
    :param response: the response of a requested game url
    :param team_id: the team_id of one of the teams playing
    :param basic_fields: fields (columns names) from basic boxscores
    :param advanced_fields: fields (columns names) from advanced boxscores
    :param season: the year of the nba season
    :return: basic and advanced boxscores (2 lists of lists) and players_id (players involved in the game)
    """
    # we get the team name based on the team id
    team = db.get_team_from_id(cursor, team_id)
    print(team)
    logging.info(f"✅Creating boxscore of team: {team}!!")
    # we get the basic boxscore table
    basic_table = bs.get_table_basic_boxscore(response, team)
    # we get the advanced boxscore table
    advanced_table = bs.get_table_advanced_boxscore(response, team)
    # we get the names of the players linked to these stats
    players = bs.get_players(basic_table)
    # we clean their names
    players = [ts.get_real_name(ts.strip_players_suffixes(player)) for player in players]
    # we get the id related to this name
    players_id = []
    for player in players:
        try:
            players_id.append(db.get_id('player', cursor, player))
        except TypeError:
            logging.error(f"""❌This player ({player}) does not appear in the roster or the salaries 
                            of the team {team} for season {season}""")
            print(f"""{player} does not appear in the roster or the salaries 
                            of the team {team} for season {season}""")

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

    return basic_boxscore, advanced_boxscore, players_id


def insert_boxscores(connection, cursor, basic_boxscore, advanced_boxscore, players_id, game_id, query_boxscores):
    """
    Insert boxscores to the boxscores table
    :param connection: the sql connection
    :param cursor: the sql cursor
    :param basic_boxscore: list of lists about basic fields boxscore
    :param advanced_boxscore: list of lists about advanced fields boxscore
    :param players_id: list of players_id involved in the game
    :param game_id: the id of the game
    :param query_boxscores: sql query to insert new rows to the table boxscore
    """
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
