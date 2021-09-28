from datetime import datetime
import pytz
import json
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import unidecode

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

def game_info(game):
    teams = [unidecode.unidecode(game['teams']['home']['team']['name']),
             unidecode.unidecode(game['teams']['away']['team']['name'])]
    lineups = scrape_lineups(teams)
    injuries = scrape_injuries(teams)
    return lineups, injuries


def scrape_lineups(teams):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'}
    players = {}
    for team in teams:
        players[team] = {}
        team_link = team.replace(" ", "-").lower()
        url = f'https://www2.dailyfaceoff.com/teams/{team_link}/line-combinations/'
        html_content = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html_content, "html.parser")
        forwards = get_players_from_table(soup, 'forwards')
        defense = get_players_from_table(soup, 'defense')
        goalies = get_players_from_table(soup, 'goalie_list')
        players[team].update(forwards)
        players[team].update(defense)
        players[team].update(goalies)
    return players


def get_players_from_table(soup, position):
    players = {position: {}}
    table = soup.find('table', id=position)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        line = row.attrs['id']
        if line not in players[position]:
            players[position].update({line: {}})
            for content in row.contents:
                if content != '\n' and 'id' in content.attrs:
                    pos = content.attrs['id']
                    name = content.find('span', attrs={'class': 'player-name'})
                    players[position][line].update({pos: name.text})
    return players


def scrape_injuries(teams):
    injuries = []
    for team in teams:
        team_injuries = {team: []}
        team_link = team.replace(" ", "-").lower()
        url = f'https://www.tsn.ca/nhl/team/{team_link}/injuries'
        session = HTMLSession()
        r = session.get(url)
        r.html.render(sleep=5)
        soup = BeautifulSoup(r.html.raw_html, "html.parser")
        try:
            soup_injuries = soup.find("div", {"class": "nfl-team-injuries"})
            rows = soup_injuries.find_all('tr')
            headers = [l for l in rows[0].text.splitlines() if l]
            headers.append('Details')
            for index, row in enumerate(rows[1:], 1):
                if index % 2 != 0:
                    details = [l for l in row.text.splitlines() if l]
                else:
                    splits = [l for l in row.text.splitlines() if l]
                    details.append(splits[0])
                if len(details) == 4:
                    injury = dict(zip(headers, details))
                    team_injuries[team].append(injury)
            injuries.append(team_injuries)
        except Exception as e:
            print(f'Unable to scrape injuries: {e}')
    return injuries


