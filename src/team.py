import os
import requests
import json
from bs4 import BeautifulSoup
import unidecode
from requests_html import HTMLSession


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


class TeamInfo:

    def __init__(self, team_info=None, team_stats=None, lineups=None, injuries=None):
        self.team_info = team_info
        self.team_stats = team_stats
        self.lineups = lineups
        self.injuries = injuries

    @classmethod
    def get_team_by_abbv(cls, abbv, teams):
        while True:
            team_info = next((team for team in teams if team['abbreviation'] == abbv), None)
            if not team_info:
                abbv = input(f"Unable to locate abbreviation {abbv} - Enter team abbv: ")
            else:
                print(f'Found {abbv}')
                return cls(team_info=team_info)

    @classmethod
    def get_team_info_by_id(cls, team_id):
        url = f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}'
        w = requests.get(url)
        team_info = json.loads(w.content)
        w.close()
        if not team_info:
            raise Exception(f'Unable to get team info from {url}')
        else:
            return cls(team_info=team_info)

    @classmethod
    def get_team_info_from_game(cls, team, away_or_home):
        if away_or_home == 'away':
            return cls(team_info=team["teams"]["away"]["team"])
        elif away_or_home == 'home':
            return cls(team_info=team["teams"]["home"]["team"])
        else:
            raise AttributeError("Please spcify 'away' or 'home'")

    def get_team_stats_by_team_id(self):
        url = f"https://statsapi.web.nhl.com/api/v1/teams/{self.team_info['id']}/stats"
        w = requests.get(url)
        team_stats = json.loads(w.content)['stats']
        w.close()
        if not team_stats:
            raise Exception(f'Unable to get team stats from {url}')
        else:
            self.team_stats = team_stats

    def scrape_lineups(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'}
        players = {}
        team_link = self.team_info['name'].replace(" ", "-").lower()
        url = f'https://www2.dailyfaceoff.com/teams/{team_link}/line-combinations/'
        html_content = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html_content, "html.parser")
        forwards = self.get_players_from_table(soup, 'forwards')
        defense = self.get_players_from_table(soup, 'defense')
        goalies = self.get_players_from_table(soup, 'goalie_list')
        players.update(forwards)
        players.update(defense)
        players.update(goalies)
        self.lineups = players

    def get_players_from_table(self, soup, position):
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

    def scrape_injuries(self):
        injuries = []
        team_link = self.team_info['name'].replace(" ", "-").lower()
        url = f'https://www.tsn.ca/nhl/team/{team_link}/injuries'
        session = HTMLSession()
        r = session.get(url)
        r.html.render(timeout=60)
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
                    injuries.append(injury)
        except Exception as e:
            print(f'Unable to scrape injuries: {e}')
        self.injuries = injuries

    def convert_team_name_to_text(self):
        self.team_info['name'] = unidecode.unidecode(self.team_info['name'])
