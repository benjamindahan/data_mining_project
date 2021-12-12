import requests
import os
import src.conf as c
from dotenv import load_dotenv

assert load_dotenv() is True

# We get from the dotenv the private keys.
host = os.getenv("host")
key = os.getenv("key")

headers = {
    'x-rapidapi-host': host,
    'x-rapidapi-key': key
}


def get_all_teams():
    """
    This function calls the API and get all the teams information.
    :return: a list of dictionaries with all the team information
    """
    response = requests.request("GET", c.URL_API_TEAMS, headers=headers).json()
    return response['api']['teams']


def get_teams_values(teams):
    """
    This function retrieves from the dictionary of information of the teams, all the relevant information.
    :param teams: a list with all the teams in the NBA
    :return: all the relevant information as a list of lists
    """
    all_teams = get_all_teams()
    teams_information = []
    teams_names_to_fix = {'BKN': 'BRK', 'PHX': 'PHO', 'CHA': 'CHO'}
    for team in all_teams:
        if team['shortName'] in teams_names_to_fix:
            team['shortName'] = teams_names_to_fix[team['shortName']]
        if team['shortName'] in teams:
            teams_information.append(
                [team['shortName'], team['city'], team['fullName'], team['leagues']['standard']['confName'],
                 team['leagues']['standard']['divName'], team['teamId']])
    return teams_information


def get_all_standings():
    """
    This function calls the API and get all the standings information.
    :return: a list of dictionaries with all the standings information
    """
    all_standings = []
    for year in range(2018, 2021):
        all_standings.append(requests.request("GET", c.URL_API_STANDINGS + str(year), headers=headers).json()['api'][
            'standings'])
    return all_standings


def get_standings(teams_dictionaries):
    """
    This function retrieves from the dictionary of information of the standings, all the relevant information.
    :param teams_dictionaries: a dictionary with the id used in the database and the id used in the API
    :return: all the relevant information as a list of lists
    """
    team_info = []
    response = get_all_standings()
    for year in response:
        for team in year:
            team['teamId'] = int(team['teamId'])
            if team['teamId'] in list(teams_dictionaries.keys()):
                team['teamId'] = teams_dictionaries[team['teamId']]
                team['seasonYear'] = int(team['seasonYear']) + 1
                team_info.append([team['teamId'], team['win'], team['loss'], team['seasonYear'],
                                  team['conference']['name'], team['conference']['rank'],
                                  team['conference']['win'], team['conference']['loss'],
                                  team['division']['name'], team['division']['rank'],
                                  team['division']['win'], team['division']['loss']])
    return team_info