import grequests
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import conf as c
import json


# Due to COVID, the last two seasons have been different
MONTHS = ["october", "november", "december", "january", "february", "march", "may", "june"]
MONTHS_2020 = ["october", "november", "december", "january", "february", "march", "july", "august", "september"]
MONTHS_2021 = ["december", "january", "february", "march", "april", "may", "june", "july"]

def double_list(list_1, list_2):
    """
    This function joins two lists by alternating values
    :param list_1: the first list to join
    :param list_2: the second list to join
    :return: the resulting list
    """
    return [x for pair in zip(list_1, list_2) for x in pair]


# We define all the lists that will be updated with the different functions
month = []
day = []
year = []
box_score = []
visitor_team = []
home_team = []

seasons = [str(year) for year in range(2008, 2022)]

list_of_urls_scores = []
for y in seasons:
    if y == "2021":
        for m in MONTHS_2021:
            url = c.URL_1_SCORE + y + c.URL_2_SCORE + m + c.URL_3_SCORE
            list_of_urls_scores.append(url)
    if y == "2020":
        for m in MONTHS_2020:
            if m == "october":
                url_2019 = c.URL_1_SCORE + y + c.URL_2_SCORE + m + "-2019" + c.URL_3_SCORE
                list_of_urls_scores.append(url_2019)
                url_2020 = c.URL_1_SCORE + y + c.URL_2_SCORE + m + "-2020" + c.URL_3_SCORE
                list_of_urls_scores.append(url_2020)
            else:
                url = c.URL_1_SCORE + y + c.URL_2_SCORE + m + c.URL_3_SCORE
                list_of_urls_scores.append(url)
    else:
        for m in MONTHS:
            url = c.URL_1_SCORE + y + c.URL_2_SCORE + m + c.URL_3_SCORE
            list_of_urls_scores.append(url)

# Making the requests with GRequests
rs = (grequests.get(url) for url in list_of_urls_scores)
responses = grequests.map(rs, size=c.BATCHES)
for url, response in zip(list_of_urls_scores, responses):
    if response is not None:
        # Creating the soup object
        soup = BeautifulSoup(response.text, "html.parser")

        # We extract all the data we need from basketball reference
        url_page = soup.find_all("a")
        url_complete = [url.get("href").strip() for url in url_page]

        # We clean the data that we scraped
        # Variable definition
        url_boxscore = []
        date = []
        box_score_aux = []
        home = []
        visitor = []
        teams = []

        # We separate in different lists to clean it: one with dates and the url and the other one with all the teams
        for url in url_complete:
            if "boxscores" in url:
                url_boxscore.append(url)
            elif "teams" in url:
                teams.append(url)

        # We separate the teams in different list: visitor or home.
        for i, team in enumerate(teams[2:]):
            if i % 2 != 0:
                visitor.append(team)
            else:
                home.append(team)

        # We separate the list in different list: date or url.
        for i, j in enumerate(url_boxscore[1:]):
            if i % 2 == 0:
                date.append(j)
            else:
                box_score_aux.append("https://www.basketball-reference.com" + j)

        # We continue with the cleaning
        box_score += box_score_aux[:-1]
        box_score_aux = box_score_aux[:-1]
        home = home[0:len(box_score_aux)]
        visitor = visitor[0:len(box_score_aux)]

        for h, v in zip(home, visitor):
            if len(h) > 17:
                h = h[7:-10]
                if len(h) == 3:
                    visitor_team.append(h)
            if len(v) > 17:
                v = v[7:-10]
                if len(v) == 3:
                    home_team.append(v)

        for url in date:
            try:
                matches = re.findall(r'(month=)(\d+)(&)(day=)(\d+)(&)(year=)(\d+)', url)[0]
                if len(matches) == 8:
                    month.append(matches[1])
                    day.append(matches[4])
                    year.append(matches[-1])
            except:
                pass

print("DAY: ", len(day))
print("BS: ", len(box_score))
print("HT: ", len(home_team))

# Checking that everything works as expected
assert len(day) == len(month)
assert len(day) == len(year)
assert len(day) == len(box_score)
assert len(day) == len(home_team)
assert len(day) == len(visitor_team)

# We double the values of the lists in order to save them properly in a dictionary
day_doubles = double_list(day, day)
month_doubles = double_list(month, month)
year_doubles = double_list(year, year)
home_team_doubles = double_list(home_team, visitor_team)
visitor_team_doubles = double_list(visitor_team, home_team)
box_score_doubles = double_list(box_score, box_score)
home_team_boolean = [1, 0] * len(day)

# We store the data extracted in a dictionary
dictionary_scores = {"day": day_doubles, "month": month_doubles, "year": year_doubles, "home_team": home_team_boolean,
                     "team": home_team_doubles, "opponent": visitor_team_doubles, "url": box_score_doubles}

# We save it as a csv file
df = pd.DataFrame(dictionary_scores)
df.to_csv("df.csv")














def get_data_grequest(urls, teams):
    """
    This function takes a list of urls and returns a list of all the request responses
    :param urls: a list of urls
    :return: a list of all the url request responses
    """
    requests = (grequests.get(u) for u in urls)
    responses = grequests.map(requests, size=10)
    return list(zip(responses, teams))




def get_basic_fields(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    team = url[-8:-5]

    team_id_basic = f"box-{team}-game-basic"

    table = soup.find_all('table', id=team_id_basic)[0]

    fields = [th.attrs['data-stat'] for th in table.find_all("th")[2:23]]

    return fields


def get_advanced_fields(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    team = url[-8:-5]

    team_id_advanced = f"box-{team}-game-advanced"

    table = soup.find_all('table', id=team_id_advanced)[0]

    fields = [th.attrs['data-stat'] for th in table.find_all("th")[2:19]]

    return fields


def get_table_basic_boxscore(response, team):
    soup = BeautifulSoup(response.content, 'html.parser')
    team_id_basic = f"box-{team}-game-basic"
    table = soup.find_all('table', id=team_id_basic)[0]
    return table

def get_table_advanced_boxscore(response, team):
    soup = BeautifulSoup(response.content, 'html.parser')
    team_id_advanced = f"box-{team}-game-advanced"
    table = soup.find_all('table', id=team_id_advanced)[0]
    return table



def get_players(table):
    players = table.find_all('a')
    return [player.get_text() for player in players]


def get_boxscore(table, fields, players):
    boxscore = dict()

    for field in fields:
        boxscore[field] = [value.get_text() for value in table.find_all("td", attrs={"data-stat": field})[:-1]]

    boxscore['player'] = players

    return boxscore


def fill_dnp(boxscore):
    num_players = len(boxscore['player'])
    num_dnp_players = num_players - len(boxscore['mp'])
    for key in boxscore:
        if key != 'player':
            boxscore[key] += ['0'] * num_dnp_players
    return boxscore


URL_RANDOM_FIELDS = 'https://www.basketball-reference.com/boxscores/201910220TOR.html'

URLS = dict_boxscores['url'][:300]
TEAMS = dict_boxscores['team'][:300]

def main():
    print('initialize')
    responses_teams = get_data_grequest(URLS, TEAMS)

    print('finish grequest')

    basic_fields = get_basic_fields(URL_RANDOM_FIELDS)
    advanced_fields = get_advanced_fields(URL_RANDOM_FIELDS)

    final_boxscores = dict()

    for response, team in responses_teams:
        print(team)
        basic_table = get_table_basic_boxscore(response, team)
        advanced_table = get_table_advanced_boxscore(response, team)

        players = get_players(basic_table)

        basic_boxscore = get_boxscore(basic_table, basic_fields, players)
        basic_boxscore = fill_dnp(basic_boxscore)

        advanced_boxscore = get_boxscore(advanced_table, advanced_fields, players)
        advanced_boxscore = fill_dnp(advanced_boxscore)

        advanced_boxscore.update(basic_boxscore)

        for key, value in advanced_boxscore.items():
            if key not in final_boxscores:
                final_boxscores[key] = value
            else:
                final_boxscores[key] += value

    with open('boxscores.json', 'w', encoding='utf8') as boxscore_file:
        json.dump(final_boxscores, boxscore_file, ensure_ascii=False)

main()