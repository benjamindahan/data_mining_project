import requests
from bs4 import BeautifulSoup
import re
import json
import csv

TEAMS = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM',
         'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']

SEASONS = ['2008', '2009', '2010', '2011', '2012', '2013', '2014',
           '2015', '2016', '2017', '2018', '2019', '2020', '2021']

OLD_TEAMS = {'BRK': {'old_name': 'NJN', 'until_season': '2012'}, 'CHO': {'old_name': 'CHA', 'until_season': '2014'},
             'NOP': {'old_name': 'NOH', 'until_season': '2013'}, 'OKC': {'old_name': 'SEA', 'until_season': '2008'}}


def get_team_summary(soup, team, season):
    """
    This function scrapes from the basketball reference page a summary of a team for a specific season (year),
    including main KPIs and results.
    :param soup: the beautiful soup object
    :param team: the team from whom the data is collected
    :param season: the season (year) for which the data is collected
    :return: a list with all the data collected, separated by attributes
    """

    text_paragraphs = soup.find_all("p")
    attributes = [attribute.getText().strip() for attribute in text_paragraphs]

    records = re.findall(r"(\d+)", attributes[2])
    n_win = records[0]
    n_loss = records[1]
    conf_ranking = records[2]

    coach_regex = re.findall(r"([A-Za-zÀ-ȕ'\s\.]+)", attributes[3][7:])
    coach = coach_regex[0]

    points = re.findall(r"(\d+\.\d+)", attributes[5])
    ppg = points[0]
    opponent_ppg = points[-1]

    paces = re.findall(r"(\d+\.\d+)", attributes[6])[-1]
    pace = paces[-1]

    rtgs = re.findall(r"(\d+\.\d+)", attributes[7])
    off_rtg = rtgs[0]
    def_rtg = rtgs[1]

    expected = re.findall(r"(\d+)", attributes[8])
    expected_win = expected[0]
    expected_loss = expected[1]
    expected_overall_ranking = expected[2]

    odds = re.findall(r"([\+|\-]\d+)", attributes[9])
    preseason_odds = odds[0]

    attendances = re.findall(r"(\d+)", attributes[10])
    attendance = attendances[0]

    try:
        playoffs = attributes[11].split("(Series Stats)")[-2]
    except:
        playoffs = "Not in playoffs"

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

    text_table = soup.find_all("table")[0].get_text()
    roster_pattern = r"(\d+)(\D+)(PF|C|PG|SF|SG)(\d+\-\d+)([A-Za-z]+) (\d+), (\d+)([a-z]+)(\d+|R)"
    roster_matches = re.findall(roster_pattern, text_table)
    roster = []
    for player in roster_matches:
        player = list(player)
        player.append(player[3][:-3])
        player.append(player[3][-3:])
        player.pop(3)
        player.insert(0, season)
        player.insert(0, team)
        roster.append(player)
    assert all([len(player) == len(roster[0]) for player in roster])
    return roster


def get_player_stats(soup, team, season, roster, team_st, season_st, name, age, g, gs, mp_per_g, fg_per_g,
                     fga_per_g, fg_pct, fg3_per_g, fg3a_per_g, fg3_pct, fg2_per_g, fg2a_per_g, fg2_pct,
                     ft_per_g, fta_per_g, ft_pct, orb_per_g, drb_per_g, trb_per_g, ast_per_g, stl_per_g, blk_per_g,
                     tov_per_g, pf_per_g, pts_per_g):
    """
    This function scrapes from the basketball reference page the players stats for a specific team on a specific season
    :param soup: the beautiful soup object
    :param team: the team from whom the data is collected
    :param season: the season for which the data are collected
    :param roster: a list with all the players from the roster
    :other params: lists to add the results
    :return: a list with all the team and opponent statistics
    """
    nr_of_players = len(roster)
    team_st += [team for i in range(nr_of_players)]
    season_st += [season for i in range(nr_of_players)]
    name += [element.get_text() for element in soup.find_all("td", {"data-stat": "player"})][:nr_of_players]
    age += [element.get_text() for element in soup.find_all("td", {"data-stat": "age"})][:nr_of_players]
    g += [element.get_text() for element in soup.find_all("td", {"data-stat": "g"})][:nr_of_players]
    gs += [element.get_text() for element in soup.find_all("td", {"data-stat": "gs"})][:nr_of_players]
    mp_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "mp_per_g"})][:nr_of_players]
    fg_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg_per_g"})][:nr_of_players]
    fga_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fga_per_g"})][:nr_of_players]
    fg_pct += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg_pct"})][:nr_of_players]
    fg3_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg3_per_g"})][:nr_of_players]
    fg3a_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg3a_per_g"})][:nr_of_players]
    fg3_pct += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg3_pct"})][:nr_of_players]
    fg2_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg2_per_g"})][:nr_of_players]
    fg2a_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg2a_per_g"})][:nr_of_players]
    fg2_pct += [element.get_text() for element in soup.find_all("td", {"data-stat": "fg2_pct"})][:nr_of_players]
    ft_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "ft_per_g"})][:nr_of_players]
    fta_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "fta_per_g"})][:nr_of_players]
    ft_pct += [element.get_text() for element in soup.find_all("td", {"data-stat": "ft_pct"})][:nr_of_players]
    orb_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "orb_per_g"})][:nr_of_players]
    drb_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "drb_per_g"})][:nr_of_players]
    trb_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "trb_per_g"})][:nr_of_players]
    ast_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "ast_per_g"})][:nr_of_players]
    stl_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "stl_per_g"})][:nr_of_players]
    blk_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "blk_per_g"})][:nr_of_players]
    tov_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "tov_per_g"})][:nr_of_players]
    pf_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "pf_per_g"})][:nr_of_players]
    pts_per_g += [element.get_text() for element in soup.find_all("td", {"data-stat": "pts_per_g"})][:nr_of_players]


def get_salaries(page_html, team, season, team_salary, season_salary, salaries, players):
    """
    This function scrapes from the basketball reference page the salaries for a team on a specific season
    :param page_html: the html of the page (in string)
    :param team: the team from whom the data is collected
    :param season: the season for which the data are collected
    :other params: lists to add the results
    :return: a list with the team and its opponents statistics
    """

    pattern_salaries_table = "<caption>Salaries Table<\/caption>[\S\s]+<\/table>"
    salaries_table = re.findall(pattern_salaries_table, page_html)[0]

    players_pattern = "([A-Za-zÀ-ȕ\.'\s]+)<\/a>"
    players_aux = re.findall(players_pattern, salaries_table)
    players += players_aux

    salaries_pattern = "\$[\d,]+"
    salaries_aux = re.findall(salaries_pattern, salaries_table)
    salaries += salaries_aux
    print(players_aux, len(players_aux), salaries_aux, len(salaries_aux))
    assert len(players_aux) == len(salaries_aux)

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

    pattern_team_opponent = "<caption>Team and Opponent Stats Table<\/caption>[\S\s]+<\/table>"
    team_opponent_table = re.findall(pattern_team_opponent, page_html)[0]

    team_opponent_stats_pattern = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+fg3\" >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\.\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" >(\d+)[\D]+fg2_pct\" >(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
    team_stats = [team] + [season] + list(re.findall(team_opponent_stats_pattern, team_opponent_table)[0])
    opponent_stats = list(re.findall(team_opponent_stats_pattern, team_opponent_table)[1])

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
    pattern_team_opponent = "<caption>Team and Opponent Stats Table<\/caption>[\S\s]+<\/table>"
    team_opponent_table = re.findall(pattern_team_opponent, page_html)[0]
    team_rank_pattern = """mp_per_g\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3_per_g\" >(\d+)[\D]+fg3a_per_g\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2_per_g\" >(\d+)[\D]+fg2a_per_g\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
    team_rank = [team] + [season] + list(re.findall(team_rank_pattern, team_opponent_table)[0])
    opponent_rank_pattern = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3\" >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
    opponent_rank = list(re.findall(opponent_rank_pattern, team_opponent_table)[0])

    assert len(team_rank) - 2 == len(opponent_rank)

    return [team_rank + opponent_rank]


def main():
    summary_year_team = [
        ["team", "season", "n_win", "n_loss", "conf_ranking", "coach", "ppg", "opponent_ppg", "pace", "off_rtg",
         "def_rtg", "expected_win",
         "expected_loss", "expected_overall_ranking", "preseason_odds", "attendance", "playoffs"]]

    rosters = [
        ["team", "season", "number", "player", "position", "month", "day", "year", "country", "experience", "height",
         "weight"]]

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

    team_salary = []
    season_salary = []
    salaries = []
    players = []

    team_opponent_stats = [
        ["team", "season", "MP_team", "FG_team", "FGA_team", "FG_per_team", "3P_team", "3PA_team", "3P_per_team",
         "2P_team", "2PA_team", "2P_per_team", "FT_team", "FTA_team", "FT_per_team", "ORB_team", "DRB_team", "TRB_team",
         "AST_team", "STL_team", "BLK_team", "TOV_team", "PF_team", "PTS_team", "MP_opp", "FG_opp", "FGA_opp",
         "FG_per_opp", "3P_opp", "3PA_opp", "3P_per_opp", "2P_opp", "2PA_opp", "2P_per_opp", "FT_opp", "FTA_opp",
         "FT_per_opp", "ORB_opp", "DRB_opp", "TRB_opp", "AST_opp", "STL_opp", "BLK_opp", "TOV_opp", "PF_opp",
         "PTS_opp"]]
    team_opponent_rank = [
        ["team", "season", "MP_team", "FG_team", "FGA_team", "FG_per_team", "3P_team", "3PA_team", "3P_per_team",
         "2P_team", "2PA_team", "2P_per_team", "FT_team", "FTA_team", "FT_per_team", "ORB_team", "DRB_team", "TRB_team",
         "AST_team", "STL_team", "BLK_team", "TOV_team", "PF_team", "PTS_team", "MP_opp", "FG_opp", "FGA_opp",
         "FG_per_opp", "3P_opp", "3PA_opp", "3P_per_opp", "2P_opp", "2PA_opp", "2P_per_opp", "FT_opp", "FTA_opp",
         "FT_per_opp", "ORB_opp", "DRB_opp", "TRB_opp", "AST_opp", "STL_opp", "BLK_opp", "TOV_opp", "PF_opp",
         "PTS_opp"]]

    for season in SEASONS:
        for team in TEAMS:
            if team in OLD_TEAMS and int(season) <= int(OLD_TEAMS[team]['until_season']):
                team = OLD_TEAMS[team]['old_name']
            print(team)
            print(season)
            url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            summary_year_team.append(get_team_summary(soup, team, season))
            assert len(summary_year_team[-1]) == len(summary_year_team[0])

            roster = get_roster(soup, team, season)
            rosters += roster

            get_player_stats(soup, team, season, roster, team_st, season_st, name, age, g, gs, mp_per_g, fg_per_g,
                             fga_per_g, fg_pct, fg3_per_g, fg3a_per_g, fg3_pct, fg2_per_g, fg2a_per_g, fg2_pct,
                             ft_per_g, fta_per_g, ft_pct, orb_per_g, drb_per_g, trb_per_g, ast_per_g, stl_per_g,
                             blk_per_g,
                             tov_per_g, pf_per_g, pts_per_g)

            page_html = str(soup.find())
            get_salaries(page_html, team, season, team_salary, season_salary, salaries, players)

            team_opponent_stats += get_team_opponent_stats(page_html, team, season)

            team_opponent_rank += get_team_opponent_rank(page_html, team, season)

    assert all([len(element) == len(team_opponent_stats[0]) for element in team_opponent_stats])
    assert all([len(element) == len(team_opponent_rank[0]) for element in team_opponent_rank])

    statistics = {'team': team_st, 'season': season_st, 'player': name, 'age': age, 'games': g,
                  'games_started': gs, 'mp_per_g': mp_per_g, 'fg_per_g': fg_per_g, 'fga_per_g': fga_per_g,
                  'fg_pct': fg_pct, 'fg3_per_g': fg3_per_g, 'fg3a_per_g': fg3a_per_g, 'fg3_pct': fg3_pct,
                  'fg2_per_g': fg2_per_g, 'fg2a_per_g': fg2a_per_g, 'fg2_pct': fg2_pct, 'ft_per_g': ft_per_g,
                  'fta_per_g': fta_per_g, 'ft_pct': ft_pct, 'orb_per_g': orb_per_g, 'drb_per_g': drb_per_g,
                  'trb_per_g': trb_per_g, 'ast_per_g': ast_per_g, 'stl_per_g': stl_per_g, 'blk_per_g': blk_per_g,
                  'tov_per_g': tov_per_g, 'pf_per_g': pf_per_g, 'pts_per_g': pts_per_g}

    assert all([len(value) == len(statistics['team']) for key, value in statistics.items()])

    salaries_dict = {'season': season_salary, 'team': team_salary, 'player': players, 'salary': salaries}

    assert all([len(value) == len(salaries_dict['team']) for key, value in salaries_dict.items()])

    with open('salaries.json', 'w', encoding='utf8') as salaries_file:
        json.dump(salaries_dict, salaries_file, ensure_ascii=False)

    with open('statistics.json', 'w', encoding='utf8') as statistics_file:
        json.dump(statistics, statistics_file, ensure_ascii=False)

    with open("rosters.csv", "w", newline="") as rosters_file:
        writer = csv.writer(rosters_file)
        writer.writerows(rosters)

    with open("summary.csv", "w", newline="") as summary_file:
        writer = csv.writer(summary_file)
        writer.writerows(summary_year_team)

    with open("team_opponent_stats.csv", "w", newline="") as team_opponent_stats_file:
        writer = csv.writer(team_opponent_stats_file)
        writer.writerows(team_opponent_stats)

    with open("team_opponent_rank.csv", "w", newline="") as team_opponent_rank_file:
        writer = csv.writer(team_opponent_rank_file)
        writer.writerows(team_opponent_rank)


if __name__ == '__main__':
    main()
