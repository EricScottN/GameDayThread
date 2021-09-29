import os
import requests
import json
from src.setup import get_env


def get_all_teams():
    url = "https://statsapi.web.nhl.com/api/v1/teams"
    w = requests.get(url)
    result = json.loads(w.content)['teams']
    w.close()
    if not result:
        raise Exception(f'Unable to get all teams from {url}')
    else:
        return result


def get_team(teams, abbv):
    while True:
        team = next((team for team in teams if team['abbreviation'] == abbv), None)
        if not team:
            abbv = input(f"Unable to locate abbreviation {abbv} - Enter team abbv: ")
        else:
            print(f'Found {abbv}')
            return team
