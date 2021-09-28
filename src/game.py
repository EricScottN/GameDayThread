from datetime import datetime
import pytz
import requests
import json


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


class Game:
    def __init__(self, game):
        self.game = game
