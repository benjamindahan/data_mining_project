import requests
from bs4 import BeautifulSoup
import re

TEAMS = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM',
         'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']

SEASONS = ['2015', '2016', '2017', '2018', '2019', '2020', '2021']


summary_year_team = []
rosters = []
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

team_opponent_stats = []
team_opponent_rank = []

for team in TEAMS:
    for season in SEASONS:
        print(team)
        print(season)
        url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

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
        summary_year_team.append([team, season, n_win, n_loss, conf_ranking, coach, ppg, opponent_ppg, pace, off_rtg, def_rtg, expected_win,
                  expected_loss, expected_overall_ranking, preseason_odds, attendance, playoffs])


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
        rosters+=roster

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




        page_html = str(soup.find())



        pattern_salaries_table = "<caption>Salaries Table<\/caption>[\S\s]+<\/table>"
        salaries_table = re.findall(pattern_salaries_table, page_html)[0]

        players_pattern = "([A-Za-zÀ-ȕ'\s]+)<\/a>"
        players_aux = re.findall(players_pattern, salaries_table)
        players += players_aux

        salaries_pattern = "\$[\d,]+"
        salaries += re.findall(salaries_pattern, salaries_table)

        team_salary += [team for i in range(len(players_aux))]
        season_salary += [season for i in range(len(players_aux))]


        pattern_team_opponent = "<caption>Team and Opponent Stats Table<\/caption>[\S\s]+<\/table>"
        team_opponent_table = re.findall(pattern_team_opponent, page_html)[0]

        team_opponent_stats_pattern = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+fg3\" >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\.\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" >(\d+)[\D]+fg2_pct\" >(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
        team_stats = [team] + [season] + list(re.findall(team_opponent_stats_pattern, team_opponent_table)[0])
        opponent_stats = list(re.findall(team_opponent_stats_pattern, team_opponent_table)[1])
        team_opponent_stats += [team_stats + opponent_stats]

        team_rank_pattern = """mp_per_g\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3_per_g\" >(\d+)[\D]+fg3a_per_g\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2_per_g\" >(\d+)[\D]+fg2a_per_g\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
        team_rank = [team] + [season] + list(re.findall(team_rank_pattern, team_opponent_table)[0])
        opponent_rank_pattern = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3\" >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
        opponent_rank = list(re.findall(opponent_rank_pattern, team_opponent_table)[0])

        team_opponent_rank += [team_rank + opponent_rank]

statistics = {'team': team_st, 'season': season_st, 'player': name, 'age': age, 'games': g,
                      'games_started': gs, 'mp_per_g': mp_per_g, 'fg_per_g': fg_per_g, 'fga_per_g': fga_per_g,
                      'fg_pct': fg_pct, 'fg3_per_g': fg3_per_g, 'fg3a_per_g': fg3a_per_g, 'fg3_pct': fg3_pct,
                      'fg2_per_g': fg2_per_g, 'fg2a_per_g': fg2a_per_g, 'fg2_pct': fg2_pct, 'ft_per_g': ft_per_g,
                      'fta_per_g': fta_per_g, 'ft_pct': ft_pct, 'orb_per_g': orb_per_g, 'drb_per_g': drb_per_g,
                      'trb_per_g': trb_per_g, 'ast_per_g': ast_per_g, 'stl_per_g': stl_per_g, 'blk_per_g': blk_per_g,
                      'tov_per_g': tov_per_g, 'pf_per_g': pf_per_g, 'pts_per_g': pts_per_g}

salaries_dict = {'season': season_salary, 'team': team_salary, 'player': players, 'salary': salaries}

