import requests
from bs4 import BeautifulSoup
import re
import src.conf as c


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


def get_team_summary(soup):
    """
    This function scrapes from the basketball reference page the team summary including main KPIs and results.
    :param soup: the beautiful soup object
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
    ppg, opponent_ppg = re.findall(c.regex_points, attributes[5])[0], re.findall(c.regex_points, attributes[5])[-1]

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
    return [n_win, n_loss, conf_ranking, coach, ppg, opponent_ppg, pace, off_rtg, def_rtg, expected_win,
            expected_loss, expected_overall_ranking, preseason_odds, attendance, playoffs]


def get_roster(soup, season):
    """
    This function scrapes from the basketball reference page the roster of a team for a specific season (year)
    :param soup: the beautiful soup object
    :param season: the season (year)
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
        if player[8] == 'R':
            player[8] = 0
        roster.append(player)

    # Checking that all works as expected
    assert all([len(player) == len(roster[0]) for player in roster])

    return roster


def strip_players_suffixes(player_name):
    """
    This function strips the player's name suffix when it exist (Jr., Sr., III, II) and returns the player's name
    Important to have consistent names, because these suffixes sometimes appear in games but not in salaries or rosters
    and vice versa.
    :param player_name: the name of a player
    :return: the name striped of its potential suffix
    """
    for suffix in c.WEIRD_PLAYER_SUFFIXES:
        if player_name.endswith(suffix):
            player_name = player_name[:-len(suffix)]
    return player_name


def get_real_name(player_name):
    """
    Some players have different names in the different tables: games, rosters, salaries...
    This is not ideal if we want to join the tables. So, based on the config file dictionary PLAYERS_NAMES_DOUBLED,
    we take the nickname (for instance 'Nene') and replace it with the real name (ie. Nene Hilario)
    :param player_name: the name of a player
    :return: the real name of the player
    """
    if player_name in c.PLAYERS_NAMES_DOUBLED:
        player_name = c.PLAYERS_NAMES_DOUBLED[player_name]
    return player_name


def get_player_stats_fields(url):
    """
    This function takes the url of any team/season on basketball-ref and returns a list of the fields (columns name)
    in the table players stats per game
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


def get_player_stats(soup, fields):
    """
    This function scrapes from the basketball reference page the players statistics of the season
    :param soup: the beautiful soup object
    :param fields: a list with all the fields (columns names) from the table players stats
    :return: a list with all the team and opponent statistics
    """
    table = soup.find_all('table', id='per_game')[0]
    players_stats = []
    for field in fields:
        players_stats.append([element.get_text() for element in table.find_all("td", {"data-stat": field})])
    return zip(*players_stats)


def get_salaries(page_html):
    """
    This function scrapes from the basketball reference page the salaries table
    :param page_html: the html of the page (in string)
    :return: a list with the team and its opponents statistics
    """

    # This table is a commented table, in order to extract the information we search with regex
    # the html text corresponding to the table.
    salaries_table = re.findall(c.regex_salaries_table, page_html)[0]

    # From the html text we look for the players' names
    players_name = re.findall(c.regex_players_salaries, salaries_table)

    # Now we are looking for the respective salaries
    salaries = re.findall(c.regex_salary_salaries, salaries_table)

    salaries = [int(salary[1:].replace(",", "")) for salary in salaries]

    return zip(players_name, salaries)


def get_team_opponent_stats(page_html):
    """
    This function scrapes from the basketball reference page the table 'team and opponents statistics'
    :param page_html: the html of the page (in string)
    :return: a list with the team and its opponents statistics
    """

    # This table is a commented table, in order to extract the information we search with regex
    # the html text corresponding to the table.
    team_opponent_table = re.findall(c.regex_team_opponent, page_html)[0]

    # From the html text we look for the statistics needed
    team_stats = list(re.findall(c.regex_team_opponent_stats, team_opponent_table)[0])
    # Slicing opponents_stats to not take min_played, already have it in teams_stats
    opponent_stats = list(re.findall(c.regex_team_opponent_stats, team_opponent_table)[1])[1:]

    # Checking that everything works as expected
    assert len(team_stats) == len(opponent_stats) + 1

    return [team_stats + opponent_stats]


def get_team_opponent_ranks(page_html):
    """
    This function scrapes from the basketball reference page the table 'team and opponents ranks'
    :param page_html: the html of the page (in string)
    :return: a list with the team and its opponents ranks
    """

    # This table is a commented table, in order to extract the information we search with regex
    # the html text corresponding to the table.
    team_opponent_table = re.findall(c.regex_team_opponent, page_html)[0]

    # From the html text we look for the statistics needed
    team_rank = list(re.findall(c.regex_team_rank, team_opponent_table)[0])
    opponent_rank = list(re.findall(c.regex_opponent_rank, team_opponent_table)[0])[1:]

    # Checking that everything works as expected
    assert len(team_rank) == len(opponent_rank) + 1

    return [team_rank + opponent_rank]
