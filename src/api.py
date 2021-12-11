import requests
import os
import src.conf as c
from dotenv import load_dotenv

assert load_dotenv() is True

host = os.getenv("host")
key = os.getenv("key")

headers = {
    'x-rapidapi-host': host,
    'x-rapidapi-key': key
}


def get_all_teams():
    response = requests.request("GET", c.URL_API_TEAMS, headers=headers).json()
    return response['api']['teams']


def get_teams_values(teams):
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
