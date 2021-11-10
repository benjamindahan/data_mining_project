URL_1 = "https://www.basketball-reference.com/teams/"
URL_2 = "/"
URL_3 = ".html"
URL_TEAMS = "https://www.basketball-reference.com/leagues/NBA_2021_games.html"

URL_1_SCORE = "https://www.basketball-reference.com/leagues/NBA_"
URL_2_SCORE = "_games-"
URL_3_SCORE = ".html"

URL_FIELDS_BOXSCORE = 'https://www.basketball-reference.com/boxscores/201910220TOR.html'

BATCHES = 20



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