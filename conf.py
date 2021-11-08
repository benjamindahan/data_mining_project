TEAMS = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM',
         'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']

SEASONS = ['2008', '2009', '2010', '2011', '2012', '2013', '2014',
           '2015', '2016', '2017', '2018', '2019', '2020', '2021']

OLD_TEAMS = {'BRK': {'old_name': 'NJN', 'until_season': '2012'}, 'CHO': {'old_name': 'CHA', 'until_season': '2014'},
             'NOP': {'old_name': 'NOH', 'until_season': '2013'}, 'OKC': {'old_name': 'SEA', 'until_season': '2008'}}

URL_1 = "https://www.basketball-reference.com/teams/"
URL_2 = "/"
URL_3 = ".html"

BATCHES = 10

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
regex_team_opponent_stats = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+fg3\" 
                            >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\.\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\"
                             >(\d+)[\D]+fg2_pct\" >(\.\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\.\d+)[\D]+(\d+)[\D]
                             +(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
regex_team_rank = """mp_per_g\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3_per_g\" 
                >(\d+)[\D]+fg3a_per_g\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2_per_g\" 
                >(\d+)[\D]+fg2a_per_g\" >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+
                (\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]
                +(\d+)[\D]+(\d+)"""
regex_opponent_rank = """mp\" >(\d+)<\/td[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+fg3\" 
                        >(\d+)[\D]+fg3a\" >(\d+)[\D]+fg3_pct\" >(\d+)[\D]+fg2\" >(\d+)[\D]+fg2a\" 
                        >(\d+)[\D]+fg2_pct\" >(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]
                        +(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)[\D]+(\d+)"""
