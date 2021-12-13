import grequests
import src.conf as c
import src.scraping_team_season as ts
import src.database_insertion as db
import src.main_functions as mf
from dotenv import load_dotenv
import os
import logging

assert load_dotenv() is True
pswd = os.getenv("password")

logging.basicConfig(filename='nba.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def main():
    """
    ----------------------------------------------INITIAL VARIABLES----------------------------------------------
    """
    # Getting all the seasons and teams
    seasons = [str(year) for year in range(c.FIRST_SEASON, c.LAST_SEASON)]
    teams = ts.get_teams()
    # Some players get cut by their team: they have a salary but they are not in the team roster
    players_cut = []

    """
    ---------------------------------------------COMMAND LINE ARGUMENTS---------------------------------------------
    """
    # Creating the command line arguments
    args = mf.get_command_line_arguments(teams)

    # We get the team names and seasons that were requested by the user
    teams = mf.verify_teams_integrity(args, teams)
    seasons = mf.verify_seasons_integrity(args, seasons)

    """
    ----------------------------------------------CONNECTION/CURSOR----------------------------------------------
    """
    # We create the database and prepare it for using it
    connection, cursor = mf.create_and_use_database(pswd)


    """
    ----------------------------------------------TEAMS----------------------------------------------
    """
    # We scrape and create the teams table of SQL
    mf.api_insert_teams(connection, cursor, teams)

    """
    --------------------------------------------------STANDINGS--------------------------------------------------------
    """
    # We scrape and create the standings table of SQL
    mf.api_insert_standings(args, connection, cursor)

    """
    ----------------------------------------------URLS/REQUESTS FOR TEAMS/SEASONS--------------------------------------
    """

    list_of_urls, responses = mf.get_urls_and_responses(seasons, teams)

    for url, response in zip(list_of_urls, responses):
        if response is not None:
            team_id, season, soup, page_html = mf.extract_info_response(response, cursor, url)

            """
            ----------------------------------------------PLAYERS----------------------------------------------
            """

            # We make sure all the players have the accurate name
            for player in ts.get_roster(soup, season):
                mf.scrape_insert_player(connection, cursor, player, players_cut)

                """
                ----------------------------------------------ROSTERS----------------------------------------------
                """
                # We scrape and create the rosters table
                mf.scrape_insert_roster(connection, cursor, args, player, team_id)

            logging.info("✅Tables rosters and players completed!!")

            """
            ----------------------------------------------SALARIES----------------------------------------------
            """
            # We scrape and create the salaries table
            mf.scrape_insert_salaries(connection, cursor, args, players_cut, page_html, season, team_id)

            """
            ----------------------------------------------TEAM SUMMARY----------------------------------------------
            """
            # We scrape and create the team summary table
            mf.scrape_insert_team_summary(connection, cursor, args, soup, season, team_id)

            """
            ----------------------------------------------PLAYER STATS----------------------------------------------
            """
            # We scrape and create the players stats
            mf.scrape_insert_players_stats(connection, cursor, args, season, team_id, soup)

            """
            ----------------------------------------------TEAMS STATS / RANKS-----------------------------------------
            """
            # We scrape and create the teams stats and ranks
            mf.scrape_insert_teams_stats_ranks(connection, cursor, args, season, team_id, page_html)

    """
    ----------------------------------------------GAMES------------------------------------------
    """
    # We scrape and create the games table
    if args.boxscores:
        cols_games = db.get_table_columns_label(cursor, 'games')
        query_games = db.create_insert_query('games', cols_games)
        for season in seasons:
            mf.scrape_insert_games(connection, cursor, query_games, season)

            """
            ----------------------------------------------BOXSCORES------------------------------------------
            """
            responses_teams_ids, basic_fields, advanced_fields, query_boxscores = \
                mf.prepare_boxscores_scraping(cursor, season)

            for response, team_id, game_id in responses_teams_ids:
                basic_boxscore, advanced_boxscore, players_id = mf.scrape_boxscores(cursor, response, team_id,
                                                                                    basic_fields, advanced_fields)

                mf.insert_boxscores(connection, cursor, basic_boxscore, advanced_boxscore, players_id, game_id,
                                    query_boxscores)

            logging.info(f"✅Table boxscores completed for season {season}!!")
        logging.info(f"✅Tables boxscores and games completed!!")
    logging.info("🚀 PROGRAM FINISHED!!")

if __name__ == '__main__':
    main()