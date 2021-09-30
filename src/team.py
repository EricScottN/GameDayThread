import os
import requests
import json
from src.setup import get_env

class NoDataFound(Exception):
    pass

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


class TeamInfo:

    def __init__(self, teams, abbv=None, team=None):
        self.teams = teams
        self.abbv = abbv
        self.team = team
        self.data = None

    @classmethod
    def get_team_by_abbv(cls, teams, abbv):
        while True:
            team = next((team for team in teams if team['abbreviation'] == abbv), None)
            if not team:
                abbv = input(f"Unable to locate abbreviation {abbv} - Enter team abbv: ")
            else:
                print(f'Found {abbv}')
                return cls(teams, abbv, team)
