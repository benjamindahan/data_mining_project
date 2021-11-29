import grequests
import requests
from bs4 import BeautifulSoup
import re
import conf as c
import json
import pandas as pd
import time



def url_creation(y):
    """
    This functions creates all the URLs that will be scraped. In each of them the year and month change.
    :param y: a list with all the seasons that will be scraped
    :return: the list of urls
    """
    list_of_urls_scores = []

# Exceptions due to COVID
    if y == "2021":
        for m in c.MONTHS_2021:
            url = c.URL_1_SCORE + y + c.URL_2_SCORE + m + c.URL_3_SCORE
            list_of_urls_scores.append(url)

    # More exceptions due to COVID
    elif y == "2020":
        for m in c.MONTHS_2020:
            if m == "october":
                url_2019 = c.URL_1_SCORE + y + c.URL_2_SCORE + m + "-2019" + c.URL_3_SCORE
                list_of_urls_scores.append(url_2019)
                url_2020 = c.URL_1_SCORE + y + c.URL_2_SCORE + m + "-2020" + c.URL_3_SCORE
                list_of_urls_scores.append(url_2020)
            else:
                url = c.URL_1_SCORE + y + c.URL_2_SCORE + m + c.URL_3_SCORE
                list_of_urls_scores.append(url)
    else:
        for m in c.MONTHS:
            url = c.URL_1_SCORE + y + c.URL_2_SCORE + m + c.URL_3_SCORE
            list_of_urls_scores.append(url)
    return list_of_urls_scores


def get_request(list_of_urls_scores):
    """
    This function creates requests with Grequest.
    :param list_of_urls_scores: the list of urls that will be requested
    :return: the responses
    """
    rs = (grequests.get(url) for url in list_of_urls_scores)
    return grequests.map(rs, size=c.BATCHES)


def double_list(list_1, list_2):
    """
    This function joins two lists by alternating values
    :param list_1: the first list to join
    :param list_2: the second list to join
    :return: the resulting list
    """
    return [x for pair in zip(list_1, list_2) for x in pair]


def extract_urls(soup):
    """
    This function scrapes the desired data
    :param soup: the bs4 object
    :return: all the urls with the data
    """
    url_page = soup.find_all("a")
    return [url.get("href").strip() for url in url_page]


def separate_lists(url_complete, url_boxscore, teams):
    """
    This function separates the extracted data into different lists to clean it:
    one with dates and the url and the other one with all the teams
    :param url_complete: the list with all the data scraped
    :param url_boxscore: the list in which the box score and date data are stored
    :param teams: the list in which the teams data is stored
    """
    for url_ in url_complete:
        if "boxscores" in url_:
            url_boxscore.append(url_)
        elif "teams" in url_:
            teams.append(url_)


def separate_teams(teams, home, visitor):
    """
    This function separates the data of the teams in two different lists to clean it:
    one with data from the visitors team and  the other one with the home teams.
    :param teams: the list with the information of all the teams
    :param home: the list in which the home teams data is stored
    :param visitor: the list in which the home visitor data is stored
    """
    for i, team in enumerate(teams[2:]):
        if i % 2 != 0:
            visitor.append(team)
        else:
            home.append(team)


def separate_date_url(url_boxscore, date, box_score_aux):
    """
    This function separates the data of the dates and boxscores in two different lists to clean it:
    one with data from the boxscore url  and the other one with the date information.
    :param url_boxscore: the list with all the information
    :param date: the list in which the date data is stored
    :param box_score_aux: the list in which the box_score data is stored
    """
    for i, j in enumerate(url_boxscore[1:]):
        if i % 2 == 0:
            date.append(j)
        else:
            box_score_aux.append("https://www.basketball-reference.com" + j)


def change_length_box_score(box_score_aux):
    """
    This function corrects the length of  box_score_aux
    :param box_score_aux: the list to correct
    :return: the corrected list
    """
    return box_score_aux[:-1]


def change_length_home(box_score_aux, home):
    """
    This function corrects the length of  home
    :param home: the list to correct
    :param box_score_aux: list with the correct length
    :return: the corrected list
    """
    return home[0:len(box_score_aux)]


def change_length_visitor(box_score_aux, visitor):
    """
    This function corrects the length of visitor
    :param visitor: the list to correct
    :param box_score_aux: list with the correct length
    :return: the corrected list
    """
    return visitor[0:len(box_score_aux)]


def clean_home_visitor(home, visitor, home_team, visitor_team):
    """
    This function cleans the home and visitor list and updates the resulting lists home_team and visitor_team
    :param home: the list to clean
    :param visitor: the list to clean
    :param home_team: the list to update
    :param visitor_team: the list to update
    """
    for h, v in zip(home, visitor):
        if len(h) > c.MAX_LENGTH:
            h = h[c.BEGINNING:c.END]
            if len(h) == c.CORRECT_LENGTH:
                visitor_team.append(h)
        if len(v) > c.MAX_LENGTH:
            v = v[c.BEGINNING:c.END]
            if len(v) == c.CORRECT_LENGTH:
                home_team.append(v)


def create_day_month_year(date, day, month, year):
    """
    This function updates the resulting lists day, month and year with data from date
    :param date: the list where the data is extracted from
    :param day: the resulting list to update
    :param month: the resulting list to update
    :param year: the resulting list to update
    """
    for url in date:
        if url != "/boxscores/":
            matches = re.findall(c.regex_date, url)[0]
            if len(matches) == c.CORRECT_LENGTH_MATCHES:
                month.append(matches[1])
                day.append(matches[4])
                year.append(matches[-1])


def scraping_urls(soup, box_score):
    # We extract all the data we need from basketball reference
    url_complete = extract_urls(soup)

    # We clean the data that we scraped
    # Variable definition
    url_boxscore = []
    date = []
    box_score_aux = []
    home = []
    visitor = []
    teams = []

    # We separate in different lists to clean it: one with dates and the url
    # and the other one with all the teams
    separate_lists(url_complete, url_boxscore, teams)

    # We separate the teams in different list: visitor or home.
    separate_teams(teams, home, visitor)

    # We separate the list in different list: date or url.
    separate_date_url(url_boxscore, date, box_score_aux)

    # Updating the resulting list box_score
    box_score += box_score_aux[:-1]

    return [box_score_aux, home, visitor, date]


def cleaning_urls(box_score_aux, home, visitor, date, home_team, visitor_team, day, month, year):
    # We clean all the list while we update them
    box_score_aux = change_length_box_score(box_score_aux)
    home = change_length_home(box_score_aux, home)
    visitor = change_length_visitor(box_score_aux, visitor)
    clean_home_visitor(home, visitor, home_team, visitor_team)
    create_day_month_year(date, day, month, year)


def doubling_lists(day, month, year, home_team, visitor_team, box_score):
    day_doubles = double_list(day, day)
    month_doubles = double_list(month, month)
    year_doubles = double_list(year, year)
    home_team_doubles = double_list(home_team, visitor_team)
    visitor_team_doubles = double_list(visitor_team, home_team)
    box_score_doubles = double_list(box_score, box_score)
    home_team_boolean = [1, 0] * len(day)
    return [day_doubles, month_doubles, year_doubles, home_team_doubles, visitor_team_doubles, home_team_boolean,
            box_score_doubles]


def get_data_grequest(urls, teams, ids):
    """
    This function takes a list of urls and returns a list of all the request responses
    :param urls: a list of urls
    :param teams: the team that played
    :param ids: the id of the team
    :return: a list of all the url request responses
    """
    requests_ = (grequests.get(u) for u in urls)
    responses = grequests.map(requests_, size=c.BATCHES_SCORES)

    # It is necessary to get a list of tuples with the url, the corresponding team and the joining id
    # because following functions will need these 3 informations
    # (cf. parameters of functions get_table_basic_boxscore and get_table_advanced_boxscore)
    return zip(responses, teams, ids)


def get_basic_fields(url):
    """
    This function takes the url of any game on basketball-ref and returns a list of the fields in a basic boxscore
    :param url: the url of any game on basketball-reference (string)
    :return: a list of the fields in a basic boxscore
    """
    # Just need to run this function once, to get the name of the basic boxscore fields
    # So the url we need can be any basketball-reference url of a nba game
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    team = url[-8:-5]  # This corresponds to the name of the team in the url: necessary to access the right table

    team_id_basic = f"box-{team}-game-basic"  # The id of the table element

    table = soup.find_all('table', id=team_id_basic)[0]  # The soup object of the basic boxscore table

    fields = [th.attrs['data-stat'] for th in table.find_all("th")[3:23]]
    # Not all the fields are relevant, hence the slicing

    return fields


def get_advanced_fields(url):
    """
    This function takes the url of any game on basketball-ref and returns a list of the fields in an advanced boxscore
    :param url: the url of any game on basketball-reference (string)
    :return: a list of the fields in an advanced boxscore
    """
    # Just need to run this function once, to get the name of the advanced boxscore fields
    # So the url we need can be any basketball-reference url of a nba game
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    team = url[-8:-5]  # This corresponds to the name of the team in the url: necessary to access the right table

    team_id_advanced = f"box-{team}-game-advanced"  # The id of the table element

    table = soup.find_all('table', id=team_id_advanced)[0]  # The soup object of the advanced boxscore table

    fields = [th.attrs['data-stat'] for th in table.find_all("th")[3:19]]
    # Not all the fields are relevant, hence the slicing

    return fields


def get_table_basic_boxscore(response, team):
    """
    This function takes a request response of a basketball-ref game url and one of the teams involved in the game
    (ex: 'MIA', 'LAL'...) and returns a soup object made of the html table of the team's basic boxscore for this game
    :param response: Response of a basketball-ref game url
    :param team: One of the teams involved in the game (ex: 'MIA', 'LAL'...)
    :return: A soup object made of the html table of the team's basic boxscore for this game
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    team_id_basic = f"box-{team}-game-basic"
    table = soup.find_all('table', id=team_id_basic)[0]
    return table


def get_table_advanced_boxscore(response, team):
    """
    This function takes a request response of a basketball-ref game url and one of the teams involved in the game
    (ex: 'MIA', 'LAL'...) and returns a soup object made of the html table of the team's advanced boxscore for this game
    :param response: Response of a basketball-ref game url
    :param team: One of the teams involved in the game (ex: 'MIA', 'LAL'...)
    :return: A soup object made of the html table of the team's advanced boxscore for this game
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    team_id_advanced = f"box-{team}-game-advanced"
    table = soup.find_all('table', id=team_id_advanced)[0]
    return table


def get_players(table):
    """
    This function takes a soup object made of an html boxscore table and returns the players listed in the boxscore
    :param table: A soup object made of an html boxscore table
    :return: A list of the players listed in the boxscore
    """
    players = table.find_all('a')
    return [player.get_text() for player in players]


def get_boxscore(table, fields, players):
    """
    This function returns a dict representing a boxscore for a specific game, for a specific team
    :param table: A soup object made of an html boxscore table (either basic or advanced)
    :param fields: A list of the fields present in the boxscore (either basic or advanced, matching the table)
    :param players: A list of the players listed in the boxscore
    :return: A dict representing a boxscore for a specific game, for a specific team
    """
    boxscore = []

    for field in fields:
        boxscore.append([value.get_text() for value in table.find_all("td", attrs={"data-stat": field})[:-1]])

    boxscore.append(players)

    return boxscore


def fill_dnp(boxscore):
    """
    This function takes a dict representing a boxscore for a specific game, for a specific team
    and returns the same dict after filling the stats of the players who did not play (dnp) with the string '0'
    :param boxscore: A dict representing a boxscore for a specific game, for a specific team
    :return: The same dict with players who did not play (dnp) having the string '0' for each field
    """
    num_players = len(boxscore[-1])
    num_dnp_players = num_players - len(boxscore[0])
    for i in range(len(boxscore) - 1):
        boxscore[i] += [None] * num_dnp_players
    return boxscore


def main():
    # We define all the lists that will be updated with the different functions
    month = []
    day = []
    year = []
    box_score = []
    visitor_team = []
    home_team = []

    # Creating the list of urls
    list_of_urls_scores = url_creation(str(c.season))

    # Making the requests with GRequests
    responses = get_request(list_of_urls_scores)

    for url, response in zip(list_of_urls_scores, responses):
        print(url)
        if response is not None:
            # Creating the soup object
            soup = BeautifulSoup(response.text, "html.parser")

            # We extract all the data we need from basketball reference
            url_complete = extract_urls(soup)

            # We clean the data that we scraped
            # Variable definition
            url_boxscore = []
            date = []
            box_score_aux = []
            home = []
            visitor = []
            teams = []

            # We separate in different lists to clean it: one with dates and the url
            # and the other one with all the teams
            separate_lists(url_complete, url_boxscore, teams)

            # We separate the teams in different list: visitor or home.
            separate_teams(teams, home, visitor)

            # We separate the list in different list: date or url.
            separate_date_url(url_boxscore, date, box_score_aux)

            # Updating the resulting list box_score
            box_score += box_score_aux[:-1]

            # We clean all the list while we update them
            box_score_aux = change_length_box_score(box_score_aux)
            home = change_length_home(box_score_aux, home)
            visitor = change_length_visitor(box_score_aux, visitor)
            clean_home_visitor(home, visitor, home_team, visitor_team)
            create_day_month_year(date, day, month, year)

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

    # We create an ID that helps us join all the data
    id_ = [i for i in range(len(box_score_doubles))]

    # We store the data extracted in a dictionary
    dictionary_scores = {"id": id_, "day": day_doubles, "month": month_doubles, "year": year_doubles,
                         "home_team": home_team_boolean,
                         "team": home_team_doubles, "opponent": visitor_team_doubles, "url": box_score_doubles}

    # Saving data into a csv file
    pd.DataFrame(dictionary_scores).to_csv("games_" + str(c.season) + ".csv")

    final_ids = dictionary_scores["id"]
    final_urls = dictionary_scores["url"]
    final_teams = dictionary_scores["team"]

    print('initialize')
    responses_teams_ids = get_data_grequest(final_urls, final_teams, final_ids)

    print('finish grequest')

    basic_fields = get_basic_fields(c.URL_FIELDS_BOXSCORE)
    advanced_fields = get_advanced_fields(c.URL_FIELDS_BOXSCORE)

    final_boxscores = dict()

    for response, team, id_ in responses_teams_ids:
        print(team)
        basic_table = get_table_basic_boxscore(response, team)
        advanced_table = get_table_advanced_boxscore(response, team)

        players = get_players(basic_table)

        basic_boxscore = get_boxscore(basic_table, basic_fields, players)
        basic_boxscore = fill_dnp(basic_boxscore)

        basic_boxscore['game_team_id'] = [id_ for _ in range(len(players))]

        advanced_boxscore = get_boxscore(advanced_table, advanced_fields, players)
        advanced_boxscore = fill_dnp(advanced_boxscore)

        basic_boxscore.update(advanced_boxscore)

        for key, value in basic_boxscore.items():
            if key not in final_boxscores:
                final_boxscores[key] = value
            else:
                final_boxscores[key] += value
        time.sleep(0.01)

    with open('boxscores_' + str(c.season) + '.json', 'w', encoding='utf8') as boxscore_file:
        json.dump(final_boxscores, boxscore_file, ensure_ascii=False)


if __name__ == "__main__":
    main()
