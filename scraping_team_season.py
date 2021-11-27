import grequests
import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import conf as c
import argparse
import os



def get_teams():
    """
    This function scrapes the name of all the teams that played in the last season of the NBA
    :return: a list of all the teams
    """

    # Making the request with Requests
    page = requests.get(c.URL_TEAMS)
    soup = BeautifulSoup(page.content, "html.parser")
    url_page = soup.find_all("a")
    url_teams = [url.get("href").strip() for url in url_page]

    # We have a list with URLs that contains the name of all the teams, we have to clean it:
    teams = []
    for url in url_teams:
        if "teams" in url and len(url) > 17:
            url = url[7:-10]
            if len(url) == 3:
                teams.append(url)
    return list(set(teams))


def get_team_summary(soup, team, season):
    """
    This function scrapes from the basketball reference page a summary of a team for a specific season (year),
    including main KPIs and results.
    :param soup: the beautiful soup object
    :param team: the team from whom the data is collected
    :param season: the season (year) for which the data is collected
    :return: a list with all the data collected, separated by attributes
    """

    # Looking for all the paragraphs in the website
    text_paragraphs = soup.find_all("p")
    attributes = [attribute.getText().strip() for attribute in text_paragraphs]

    # Getting the records and ranking from the summary
    n_win, n_loss, conf_ranking = re.findall(c.regex_numbers, attributes[2])[0:3]

    # Getting the coach from the summary
    coach = re.findall(c.regex_coach, attributes[3][7:])[0]

    # Getting the points per game
    ppg, opponent_ppg = re.findall(c.regex_points, attributes[5])[0],re.findall(c.regex_points, attributes[5])[-1]

    # Getting the pace
    pace = re.findall(c.regex_paces, attributes[6])[-1][-1]

    # Getting the rating
    off_rtg, def_rtg = re.findall(c.regex_rtgs, attributes[7])[0:2]

    # Getting the expected results
    expected_win, expected_loss, expected_overall_ranking = re.findall(c.regex_numbers, attributes[8])[0:3]

    # Getting the preseason odds
    preseason_odds = re.findall(c.regex_odds, attributes[9])[0]

    # Getting the attendances
    attendance = re.findall(c.regex_numbers, attributes[10])[0]

    # Getting the playoffs information
    try:
        playoffs = attributes[11].split("(Series Stats)")[-2]
    except IndexError:
        playoffs = "Not in playoffs"

    # Returning a list with all the attributes
    return [team, season, n_win, n_loss, conf_ranking, coach, ppg, opponent_ppg, pace, off_rtg, def_rtg, expected_win,
            expected_loss, expected_overall_ranking, preseason_odds, attendance, playoffs]


def get_roster(soup, team, season):
    """
    This function scrapes from the basketball reference page the roster of a team for a specific season (year)
    :param soup: the beautiful soup object
    :param team: the team from whom the data is collected
    :param season: the season (year) for which the data are collected
    :return: a list with all the players from roster + their attributes
    """

    # Getting the first table (Rosters table) from the website
    text_table = soup.find_all("table")[0].get_text()

    # Getting all the attributes from the table
    roster_matches = re.findall(c.regex_rosters, text_table)
    roster = []

    # Cleaning the attributes
    for player in roster_matches:
        player = list(player)
        player.append(player[3][:-3])
        player.append(player[3][-3:])
        player.pop(3)
        player.insert(0, season)
        player.insert(0, team)
        print(player)
        if player[9] == 'R':
            player[9] = 0
        roster.append(player)

    # Checking that all works as expected
    assert all([len(player) == len(roster[0]) for player in roster])

    return roster

def get_player_stats_fields(url):
    """
    This function takes the url of any team/season on basketball-ref and returns a list of the fields in the table
    players stats per game
    :param url: the url of team/season on basketball-reference (string)
    :return: a list of the fields in a basic boxscore
    """
    # Just need to run this function once, to get the name of the basic boxscore fields
    # So the url we need can be any basketball-reference url of a nba game
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find_all('table', id='per_game')[0]  # The soup object of the basic boxscore table
    fields = [th.attrs['data-stat'] for th in table.find_all("th")[1:28]]
    # Not all the fields are relevant, hence the slicing

    return fields

def get_player_stats(soup, team, season, roster, team_st, season_st, fields, *args):
    """
    This function scrapes from the basketball reference page the players stats for a specific team on a specific season
    :param soup: the beautiful soup object
    :param team: the team from whom the data is collected
    :param season: the season for which the data are collected
    :param roster: a list with all the players from the roster
    :other params: lists to add the results
    :return: a list with all the team and opponent statistics
    """

    # In order to get the information from the statistics we scrape attribute by attribute
    nr_of_players = len(roster)
    team_st += [team for i in range(nr_of_players)]
    season_st += [season for i in range(nr_of_players)]

    for field, arg in zip(fields, args):
        arg += [element.get_text() for element in soup.find_all("td", {"data-stat": field})][:nr_of_players]


def get_salaries(page_html, team, season, team_salary, season_salary, salaries, players):
    """
    This function scrapes from the basketball reference page the salaries for a team on a specific season
    :param page_html: the html of the page (in string)
    :param team: the team from whom the data is collected
    :param season: the season for which the data are collected
    :other params: lists to add the results
    :return: a list with the team and its opponents statistics
    """

    # This table is a commented table, in order to extract the information we search with regex
    # the html text corresponding to the table.
    salaries_table = re.findall(c.regex_salaries_table, page_html)[0]

    # From the html text we look for the players' names
    players_aux = re.findall(c.regex_players_salaries, salaries_table)

    # Now we are looking for the respective salaries
    salaries_aux = re.findall(c.regex_salary_salaries, salaries_table)

    # Corrections for some specific cases in which there is no salary information
    diff_players_salaries = len(players_aux) - len(salaries_aux)
    if diff_players_salaries > 0:
        salaries_aux += [None] * diff_players_salaries
    else:
        players_aux += [None] * diff_players_salaries

    # Updating the lists of salaries and players
    players += players_aux
    salaries += salaries_aux

    # Checking that we have the salary of every player
    assert len(players_aux) == len(salaries_aux)

    # Adding season and teams
    team_salary += [team for i in range(len(players_aux))]
    season_salary += [season for i in range(len(players_aux))]


def get_team_opponent_stats(page_html, team, season):
    """
    This function scrapes from the basketball reference page the team and opponents statistics for a team
    on a specific season
    :param page_html: the html of the page (in string)
    :param team: the team from whom the data is collected
    :param season: the season for which the data are collected
    :return: a list with the team and its opponents statistics
    """

    # This table is a commented table, in order to extract the information we search with regex
    # the html text corresponding to the table.
    team_opponent_table = re.findall(c.regex_team_opponent, page_html)[0]

    # From the html text we look for the statistics needed
    team_stats = [team] + [season] + list(re.findall(c.regex_team_opponent_stats, team_opponent_table)[0])
    opponent_stats = list(re.findall(c.regex_team_opponent_stats, team_opponent_table)[1])

    # Checking that everything works as expected
    assert len(team_stats) - 2 == len(opponent_stats)

    return [team_stats + opponent_stats]


def get_team_opponent_rank(page_html, team, season):
    """
    This function scrapes from the basketball reference page the team and opponents ranks for a team
    on a specific season
    :param page_html: the html of the page (in string)
    :param team: the team from whom the data is collected
    :param season: the season for which the data are collected
    :return: a list with the team and its opponents ranks
    """

    # This table is a commented table, in order to extract the information we search with regex
    # the html text corresponding to the table.
    team_opponent_table = re.findall(c.regex_team_opponent, page_html)[0]

    # From the html text we look for the statistics needed
    team_rank = [team] + [season] + list(re.findall(c.regex_team_rank, team_opponent_table)[0])
    opponent_rank = list(re.findall(c.regex_opponent_rank, team_opponent_table)[0])

    # Checking that everything works as expected
    assert len(team_rank) - 2 == len(opponent_rank)

    return [team_rank + opponent_rank]


def main():
    # We get all the team names
    teams = get_teams()

    # We get all the seasons from 2008 to 2021
    seasons = [str(year) for year in range(2008, 2022)]

    parser = argparse.ArgumentParser(description='Get data about NBA teams/seasons')
    parser.add_argument('data_type', nargs=1, choices=['summary', 'roster', 'players_stats', 'team_stats',
                                                       'team_ranks', 'salaries', 'all'],
                        help='The type of data you want to scrape')
    parser.add_argument('-t', nargs='*', default='all',
                        help=f"""The teams you want to get data from. Choose between these teams: 
                            {teams}. By default, all the teams are used.
                            Example: -t MIA LAL""")
    parser.add_argument('-s', nargs='*', default='all',
                        help='The seasons you want to get data from. Choose seasons between 2008 and 2021.'
                             'By default, all the seasons are used.'
                             'Example: -s 2010 2015')

    args = parser.parse_args()

    # We get the team names that were requested by the user
    if args.t != 'all':
        teams = args.t

    # We get all the seasons requested by the user
    if args.s != 'all':
        seasons = args.s
    # First we define all the lists that will be updated with the different functions

    # For the get_team_summary function
    summary_year_team = [
        ["team", "season", "n_win", "n_loss", "conf_ranking", "coach", "ppg", "opponent_ppg", "pace", "off_rtg",
         "def_rtg", "expected_win",
         "expected_loss", "expected_overall_ranking", "preseason_odds", "attendance", "playoffs"]]
    # For the get_roster function
    rosters = [
        ["team", "season", "number", "player", "position", "month", "day", "year", "country", "experience", "height",
         "weight"]]

    # For the get_player_stats function
    fields = get_player_stats_fields('https://www.basketball-reference.com/teams/BRK/2022.html')
    season_st = []
    team_st = []
    name = []
    age = []
    g = []
    gs = []
    mp_per_g = []
    fg_per_g = []
    fga_per_g = []
    fg_pct = []
    fg3_per_g = []
    fg3a_per_g = []
    fg3_pct = []
    fg2_per_g = []
    fg2a_per_g = []
    fg2_pct = []
    efg_pct = []
    ft_per_g = []
    fta_per_g = []
    ft_pct = []
    orb_per_g = []
    drb_per_g = []
    trb_per_g = []
    ast_per_g = []
    stl_per_g = []
    blk_per_g = []
    tov_per_g = []
    pf_per_g = []
    pts_per_g = []

    # For the get_salary function
    team_salary = []
    season_salary = []
    salaries = []
    players = []

    # For the get_team_opponent_stats function
    team_opponent_stats = [
        ["team", "season", "MP_team", "FG_team", "FGA_team", "FG_per_team", "3P_team", "3PA_team", "3P_per_team",
         "2P_team", "2PA_team", "2P_per_team", "FT_team", "FTA_team", "FT_per_team", "ORB_team", "DRB_team", "TRB_team",
         "AST_team", "STL_team", "BLK_team", "TOV_team", "PF_team", "PTS_team", "MP_opp", "FG_opp", "FGA_opp",
         "FG_per_opp", "3P_opp", "3PA_opp", "3P_per_opp", "2P_opp", "2PA_opp", "2P_per_opp", "FT_opp", "FTA_opp",
         "FT_per_opp", "ORB_opp", "DRB_opp", "TRB_opp", "AST_opp", "STL_opp", "BLK_opp", "TOV_opp", "PF_opp",
         "PTS_opp"]]

    # For the get_team_opponent_rank function
    team_opponent_rank = [
        ["team", "season", "MP_team", "FG_team", "FGA_team", "FG_per_team", "3P_team", "3PA_team", "3P_per_team",
         "2P_team", "2PA_team", "2P_per_team", "FT_team", "FTA_team", "FT_per_team", "ORB_team", "DRB_team", "TRB_team",
         "AST_team", "STL_team", "BLK_team", "TOV_team", "PF_team", "PTS_team", "MP_opp", "FG_opp", "FGA_opp",
         "FG_per_opp", "3P_opp", "3PA_opp", "3P_per_opp", "2P_opp", "2PA_opp", "2P_per_opp", "FT_opp", "FTA_opp",
         "FT_per_opp", "ORB_opp", "DRB_opp", "TRB_opp", "AST_opp", "STL_opp", "BLK_opp", "TOV_opp", "PF_opp",
         "PTS_opp"]]

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

            # Calling all the functions
            if args.data_type[0] in ['summary', 'all']:
                summary_year_team.append(get_team_summary(soup, team, season))

                # Checking that everything works as expected
                assert len(summary_year_team[-1]) == len(summary_year_team[0])

            if args.data_type[0] in ['roster', 'all']:
                roster = get_roster(soup, team, season)
                rosters += roster

            if args.data_type[0] in ['players_stats', 'all']:
                roster = get_roster(soup, team, season)
                get_player_stats(soup, team, season, roster, team_st, season_st, fields, name, age, g, gs, mp_per_g, fg_per_g,
                             fga_per_g, fg_pct, fg3_per_g, fg3a_per_g, fg3_pct, fg2_per_g, fg2a_per_g, fg2_pct,
                             efg_pct, ft_per_g, fta_per_g, ft_pct, orb_per_g, drb_per_g, trb_per_g, ast_per_g, stl_per_g,
                             blk_per_g,
                             tov_per_g, pf_per_g, pts_per_g)

            if args.data_type[0] in ['salaries', 'team_stats', 'team_ranks', 'all']:
                page_html = str(soup.find())

                if args.data_type[0] in ['salaries', 'all']:
                    get_salaries(page_html, team, season, team_salary, season_salary, salaries, players)

                if args.data_type[0] in ['team_stats', 'all']:
                    team_opponent_stats += get_team_opponent_stats(page_html, team, season)
                    # Checking that everything works as expected
                    assert all([len(element) == len(team_opponent_stats[0]) for element in team_opponent_stats])

                if args.data_type[0] in ['team_ranks', 'all']:
                    team_opponent_rank += get_team_opponent_rank(page_html, team, season)
                    # Checking that everything works as expected
                    assert all([len(element) == len(team_opponent_rank[0]) for element in team_opponent_rank])

    if args.data_type[0] in ['players_stats', 'all']:
        # Creating a dictionary with all the lists updating as result of calling the function get_statistics
        statistics = {'team': team_st, 'season': season_st, 'player': name, 'age': age, 'games': g,
                  'games_started': gs, 'mp_per_g': mp_per_g, 'fg_per_g': fg_per_g, 'fga_per_g': fga_per_g,
                  'fg_pct': fg_pct, 'fg3_per_g': fg3_per_g, 'fg3a_per_g': fg3a_per_g, 'fg3_pct': fg3_pct,
                  'fg2_per_g': fg2_per_g, 'fg2a_per_g': fg2a_per_g, 'fg2_pct': fg2_pct, 'ft_per_g': ft_per_g,
                  'fta_per_g': fta_per_g, 'ft_pct': ft_pct, 'orb_per_g': orb_per_g, 'drb_per_g': drb_per_g,
                  'trb_per_g': trb_per_g, 'ast_per_g': ast_per_g, 'stl_per_g': stl_per_g, 'blk_per_g': blk_per_g,
                  'tov_per_g': tov_per_g, 'pf_per_g': pf_per_g, 'pts_per_g': pts_per_g}

        # Checking that everything works as expected
        assert all([len(value) == len(statistics['team']) for key, value in statistics.items()])

        filename = 'team_season/statistics.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open('team_season/statistics.json', 'w', encoding='utf8') as statistics_file:
            json.dump(statistics, statistics_file, ensure_ascii=False)

    if args.data_type[0] in ['salaries', 'all']:
        # Creating a dictionary with all the lists updating as result of calling the function get_salaries
        salaries_dict = {'season': season_salary, 'team': team_salary, 'player': players, 'salary': salaries}

        # Checking that everything works as expected
        for key, value in salaries_dict.items():
            print(key, len(value))

        assert all([len(value) == len(salaries_dict['team']) for key, value in salaries_dict.items()])

        # Saving the scraped information in json files or csv files as convenient.
        with open('team_season/salaries.json', 'w', encoding='utf8') as salaries_file:
            json.dump(salaries_dict, salaries_file, ensure_ascii=False)

    if args.data_type[0] in ['roster', 'all']:
        with open("team_season/rosters.csv", "w", newline="") as rosters_file:
            writer = csv.writer(rosters_file)
            writer.writerows(rosters)

    if args.data_type[0] in ['summary', 'all']:
        with open("team_season/summary.csv", "w", newline="") as summary_file:
            writer = csv.writer(summary_file)
            writer.writerows(summary_year_team)

    if args.data_type[0] in ['team_stats', 'all']:
        with open("team_season/team_opponent_stats.csv", "w", newline="") as team_opponent_stats_file:
            writer = csv.writer(team_opponent_stats_file)
            writer.writerows(team_opponent_stats)

    if args.data_type[0] in ['team_ranks', 'all']:
        with open("team_season/team_opponent_rank.csv", "w", newline="") as team_opponent_rank_file:
            writer = csv.writer(team_opponent_rank_file)
            writer.writerows(team_opponent_rank)


if __name__ == '__main__':
    main()