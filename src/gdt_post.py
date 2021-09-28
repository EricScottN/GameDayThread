from datetime import datetime, timedelta
import time
import pytz
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import unidecode

utc = pytz.timezone('UTC')
eastern = pytz.timezone('US/Eastern')


def find_gdt(team_name, subreddit):
    from src.setup import Reddit
    r = Reddit().reddit
    gdt_post = None
    user = r.redditor(r.user.me().name)
    posts = [x for x in user.submissions.new(limit=20)]
    for post in posts:
        made = utc.localize(datetime.utcfromtimestamp(post.created_utc)).astimezone(eastern)
        # If "Game Thread" and my_team in post title and subreddit is hockey and date made is today
        if team_name in post.title and 'Game Thread' in post.title \
                and post.subreddit.display_name.lower() == subreddit \
                and made.strftime('%d%m%Y') == datetime.now(eastern).strftime('%d%m%Y'):
            print(f'Game Day Thread Found - {post.title}')
            gdt_post = post
            break
    return gdt_post


def can_post(game):
    pretime = timedelta(hours=2)
    gametime_ordinal = datetime.fromisoformat(game['gameDate'][:-1]) - datetime.now().utcnow()
    if gametime_ordinal.total_seconds() <= 0:
        print("Game has already started. Cannot Post Game Day Thread")
        return
    while gametime_ordinal > pretime:
        min, sec = divmod((gametime_ordinal - pretime).seconds, 60)
        hour, min = divmod(min, 60)
        print(f'Sleeping for {hour} hours {min} minutes until able to post')
        time.sleep((gametime_ordinal - pretime).seconds)
    else:
        return game_info(game)




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

