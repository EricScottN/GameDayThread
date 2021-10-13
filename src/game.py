from datetime import datetime
import pytz
import json
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import unidecode
from src.team import TeamInfo

class NoGamesFoundError(Exception):

    def __init__(self, team_name):
        self.team_name = team_name

    def __str__(self):
        return f'Could not find games for {self.team_name}'


def get_today_games():
    eastern = pytz.timezone('US/Eastern')
    today = datetime.now(eastern).strftime('%Y-%m-%d')
    domain = 'https://statsapi.web.nhl.com'
    url = f'{domain}/api/v1/schedule?startDate={today}&endDate={today}&expand=schedule.teams,' \
          f'schedule.linescore'
    w = requests.get(url)
    games = json.loads(w.content)['dates'][0]['games']
    w.close()
    if not games:
        raise Exception(f'Unable to return games from {url}')
    else:
        return games


def get_game_by_team_id(games, my_team):
    game = next((game for game in games if game['teams']['away']['team']['id'] == my_team['id'] or
                 game['teams']['home']['team']['id'] == my_team['id']), None)
    return game


class GameInfo():

    def __init__(self, game_info=None, away_team=None, home_team=None, game_content=None):
        self.game_info = game_info
        self.away_team = away_team
        self.home_team = home_team
        self.game_content = game_content
        self.final = False

    @classmethod
    def create_with_games_and_team(cls, games, team):
        game_info = next((game for game in games if game['teams']['away']['team']['id'] == team['id'] or
                          game['teams']['home']['team']['id'] == team['id']), None)
        if not game_info:
            raise NoGamesFoundError(team_name=team['name'])
        return cls(game_info=game_info,
                   away_team=TeamInfo.get_team_info_from_game(game_info, 'away'),
                   home_team=TeamInfo.get_team_info_from_game(game_info, 'home'))

    def get_game_content(self):
        domain = 'https://statsapi.web.nhl.com'
        url = f"{domain}{self.game_info['content']['link']}"
        w = requests.get(url)
        game_content = json.loads(w.content)
        w.close()
        if not game_content:
            raise Exception(f'Unable to return games from {url}')
        else:
            self.game_content=game_content









