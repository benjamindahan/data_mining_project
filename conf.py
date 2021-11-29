URL_1 = "https://www.basketball-reference.com/teams/"
URL_2 = "/"
URL_3 = ".html"
URL_TEAMS = "https://www.basketball-reference.com/leagues/NBA_2021_games.html"

URL_1_SCORE = "https://www.basketball-reference.com/leagues/NBA_"
URL_2_SCORE = "_games-"
URL_3_SCORE = ".html"

URL_FIELDS_PLAYER_STATS = 'https://www.basketball-reference.com/teams/LAC/2010.html'
URL_FIELDS_BOXSCORE = 'https://www.basketball-reference.com/boxscores/201910220TOR.html'

BATCHES = 20
BATCHES_SCORES = 1500

FIRST_SEASON = 2008
LAST_SEASON = 2022

season = 2020

# Due to COVID, the last two seasons have been different
MONTHS = ["october", "november", "december", "january", "february", "march", "may", "june"]
MONTHS_2020 = ["october", "november", "december", "january", "february", "march", "july", "august", "september"]
MONTHS_2021 = ["december", "january", "february", "march", "april", "may", "june", "july"]

regex_numbers = r"(\d+)"
regex_coach = r"([A-Za-zÀ-ȕ'\s\.]+)"
regex_points = r"(\d+\.\d+)"
regex_paces = r"(\d+\.\d+)"
regex_rtgs = r"(\d+\.\d+)"
regex_odds = r"([\+|\-]\d+)"
regex_rosters = r"(\d+)(\D+)(PF|C|PG|SF|SG)(\d+\-\d+)([A-Za-z]+) (\d+), (\d+)([a-z]+)(\d+|R)"
regex_salaries_table = "<caption>Salaries Table<\/caption>[\S\s]+<\/table>"
regex_players_salaries = "([A-Za-zÀ-ȕ\.'\s]+)(?:<\/a>|<\/td>)"
regex_salary_salaries = "\$[\d,]+"
regex_team_opponent = "<caption>Team and Opponent Stats Table<\/caption>[\S\s]+<\/table>"
regex_team_opponent_stats = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+fg3\" >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\.\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" >(\d+)[\D]+fg2_pct\" >(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
regex_team_rank = """mp_per_g\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3_per_g\" >(\d+)[\D]+fg3a_per_g\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2_per_g\" >(\d+)[\D]+fg2a_per_g\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
regex_opponent_rank = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3\" >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""

regex_date = r'(month=)(\d+)(&)(day=)(\d+)(&)(year=)(\d+)'

MAX_LENGTH = 17
BEGINNING = 7
END = -10
CORRECT_LENGTH = 3
CORRECT_LENGTH_MATCHES = 8

OLD_TEAMS = {'BRK': {'old_name': 'NJN', 'until_season': '2012'}, 'CHO': {'old_name': 'CHA', 'until_season': '2014'},
             'NOP': {'old_name': 'NOH', 'until_season': '2013'}, 'OKC': {'old_name': 'SEA', 'until_season': '2008'}}

OLD_TEAMS_LABELS = ['NJN', 'CHA', 'SEA', 'NOH']

INDEXES_PLAYERS = [2, 4, 5, 6, 7, 9, 10]
INDEXES_ROSTERS = [0, 1, 3, 8]

PLAYERS_NAMES = ['D.J. Mbenga', 'Gigi Datome', 'Vítor Luiz Faverani', 'Wendell Carte', 'aren Jackson', 'Mo Bamba', 'Didi Louzada']

PLAYERS_NAMES_DOUBLED = {'Mbenga': 'Didier Ilunga-Mbenga',
                         'D.J. Mbenga': 'Didier Ilunga-Mbenga',
                         'Gigi Datome': 'Luigi Datome',
                         'Vítor Luiz Faverani': 'Vítor Faverani',
                         'Wendell Carte': 'Wendell Carter',
                         'aren Jackson': 'Jaren Jackson',
                         'Mo Bamba': 'Mohamed Bamba',
                         'Didi Louzada': 'Marcos Louzada Silva'}

WEIRD_PLAYER_SUFFIXES = [' Jr.', ' Sr.', ' III', ' II']

FIRST_SEASON_MONTH = 10
LAST_SEASON_MONTH = 7

LAST_SEASON_MONTH_2020 = 10