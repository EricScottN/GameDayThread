import os
import json
from datetime import datetime, timedelta
import time
import pytz
import requests
import html
from src.setup import Reddit, get_env, args

utc = pytz.timezone('UTC')
eastern = pytz.timezone('US/Eastern')

r = Reddit().reddit
user = r.redditor(r.user.me().name)
if args.subreddit:
    subreddit = r.subreddit(args.subreddit)
else:
    subreddit = r.subreddit(get_env('SUBREDDIT'))

teams = {'SEA': ['/r/seattlekraken', 'Seattle', 'Kraken'],
         'VGK': ['/r/goldenknights', 'Vegas', 'Golden Knights'],
         'MIN': ['/r/wildhockey', 'Minnesota', 'Wild'], 'TOR': ['/r/leafs', 'Toronto', 'Leafs'],
         'WSH': ['/r/caps', 'Washington', 'Capitals'], 'BOS': ['/r/bostonbruins', 'Boston', 'Bruins'],
         'DET': ['/r/detroitredwings', 'Detroit', 'Red Wings'],
         'NYI': ['/r/newyorkislanders', 'New York', 'Islanders'],
         'FLA': ['/r/floridapanthers', 'Florida', 'Panthers'],
         'COL': ['/r/coloradoavalanche', 'Colorado', 'Avalanche'],
         'NSH': ['/r/predators', 'Nashville', 'Predators'], 'CHI': ['/r/hawks', 'Chicago', 'Blackhawks'],
         'NJD': ['/r/devils', 'New Jersey', 'Devils'], 'DAL': ['/r/dallasstars', 'Dallas', 'Stars'],
         'CGY': ['/r/calgaryflames', 'Calgary', 'Flames'], 'NYR': ['/r/rangers', 'New York', 'Rangers'],
         'CAR': ['/r/canes', 'Carolina', 'Hurricanes'], 'WPG': ['/r/winnipegjets', 'Winnipeg', 'Jets'],
         'BUF': ['/r/sabres', 'Buffalo', 'Sabres'], 'VAN': ['/r/canucks', 'Vancouver', 'Canucks'],
         'STL': ['/r/stlouisblues', 'St Louis', 'Blues'],
         'SJS': ['/r/sanjosesharks', 'San Jose', 'Sharks'], 'MTL': ['/r/habs', 'Montreal', 'Canadiens'],
         'PHI': ['/r/flyers', 'Philadelphia', 'Flyers'], 'ANA': ['/r/anaheimducks', 'Anaheim', 'Ducks'],
         'LAK': ['/r/losangeleskings', 'Los Angeles', 'Kings'],
         'CBJ': ['/r/bluejackets', 'Columbus', 'Blue Jackets'],
         'PIT': ['/r/penguins', 'Pittsburgh', 'Penguins'],
         'EDM': ['/r/edmontonoilers', 'Edmonton', 'Oilers'],
         'TBL': ['/r/tampabaylightning', 'Tampa Bay', 'Lightning'],
         'ARI': ['/r/coyotes', 'Arizona', 'Coyotes'], 'OTT': ['/r/ottawasenators', 'Ottawa', 'Senators']}
convert = {'Vegas Golden Knights': 'VGK', 'San Jose Sharks': 'SJS', 'Detroit Red Wings': 'DET',
           'Arizona Coyotes': 'ARI', 'Carolina Hurricanes': 'CAR', 'Toronto Maple Leafs': 'TOR',
           'Boston Bruins': 'BOS', 'Florida Panthers': 'FLA', 'Columbus Blue Jackets': 'CBJ',
           'Anaheim Ducks': 'ANA', 'Buffalo Sabres': 'BUF', 'Montreal Canadiens': 'MTL',
           'Edmonton Oilers': 'EDM', 'Pittsburgh Penguins': 'PIT', 'New York Rangers': 'NYR',
           'Washington Capitals': 'WSH', 'St Louis Blues': 'STL', 'Colorado Avalanche': 'COL',
           'Minnesota Wild': 'MIN', 'Dallas Stars': 'DAL', 'Winnipeg Jets': 'WPG',
           'New Jersey Devils': 'NJD', 'Tampa Bay Lightning': 'TBL', 'Los Angeles Kings': 'LAK',
           'Calgary Flames': 'CGY', 'Chicago Blackhawks': 'CHI', 'New York Islanders': 'NYI',
           'Nashville Predators': 'NSH', 'Ottawa Senators': 'OTT', 'Vancouver Canucks': 'VAN',
           'Philadelphia Flyers': 'PHI', 'Seattle Kraken': 'SEA'}


def construct_split():
    return f"***\n"


def find_gdt(team_name):
    gdt_post = None
    posts = [x for x in user.submissions.new(limit=20)]
    for post in posts:
        made = utc.localize(datetime.utcfromtimestamp(post.created_utc)).astimezone(eastern)
        # If "Game Thread" and my_team in post title and subreddit is hockey and date made is today
        if team_name in post.title and 'Game' in post.title and 'Thread' in post.title \
                and post.subreddit.display_name.lower() == subreddit \
                and made.strftime('%d%m%Y') == datetime.now(eastern).strftime('%d%m%Y'):
            print(f'Game Day Thread Found - {post.title}')
            gdt_post = post
            break
    return gdt_post


def can_post(game):
    pretime = timedelta(hours=1.5)
    gametime_ordinal = datetime.fromisoformat(game['gameDate'][:-1]) - datetime.now().utcnow()
    if gametime_ordinal.total_seconds() <= 0:
        return False
    while gametime_ordinal > pretime:
        min, sec = divmod((gametime_ordinal - pretime).seconds, 60)
        hour, min = divmod(min, 60)
        print(f'Sleeping for {hour} hours {min} minutes until able to post')
        time.sleep((gametime_ordinal - pretime).seconds)
        gametime_ordinal = datetime.fromisoformat(game['gameDate'][:-1]) - datetime.now().utcnow()
    else:
        return True


def save_markdown(all_text, file_name):
    if not os.path.isdir("./log/"):
        os.makedirs("./log/")
    text_file = open(f"./log/{file_name}.txt", "w")
    for element in all_text:
        text_file.write(element + "\n")
    text_file.close()


def generate_markdown_for_gdt(game):
    game_info = game.game_info
    away_team_info = game.away_team.team_info
    away_team_stats = game.away_team.team_stats
    away_team_lineup = game.away_team.lineups
    away_team_injuries = game.away_team.injuries
    home_team_info = game.home_team.team_info
    home_team_stats = game.home_team.team_stats
    home_team_linup = game.home_team.lineups
    home_team_injuries = game.home_team.injuries
    time = datetime.fromisoformat(game_info['gameDate'][:-1])
    utc_time = pytz.utc.localize(time, is_dst=None)
    at_time = utc_time.astimezone(pytz.timezone('Canada/Atlantic'))
    et_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
    ct_time = utc_time.astimezone(pytz.timezone("US/Central"))
    mt_time = utc_time.astimezone(pytz.timezone('US/Mountain'))
    pt_time = utc_time.astimezone(pytz.timezone('US/Pacific'))
    home_team_time = utc_time.astimezone(pytz.timezone(home_team_info['venue']['timeZone']['id']))
    all_text = []

    def construct_title():
        title = f"Game Day Thread: " \
                f"{away_team_info['name']} at " \
                f"{home_team_info['name']} - " \
                f"{home_team_time:%d %b %Y - %I:%M%p} {home_team_info['venue']['timeZone']['tz']}"
        if args.title:
            title += f' - {args.title}'

        return title

    def construct_header():
        header = f"#{away_team_info['name']} []({teams[away_team_info['abbreviation']][0]})" \
                 f"({away_team_stats[0]['splits'][0]['stat']['wins']}-" \
                 f"{away_team_stats[0]['splits'][0]['stat']['losses']}-" \
                 f"{away_team_stats[0]['splits'][0]['stat']['ot']}) at " \
                 f"{home_team_info['name']} []({teams[home_team_info['abbreviation']][0]})" \
                 f"({home_team_stats[0]['splits'][0]['stat']['wins']}-" \
                 f"{home_team_stats[0]['splits'][0]['stat']['losses']}-" \
                 f"{home_team_stats[0]['splits'][0]['stat']['ot']})"

        return header

    def construct_time_table():
        time_table = f"##Time\n" \
                     f"|PT|MT|CT|ET|AT|\n" \
                     f"|:--:|:--:|:--:|:--:|:--:|\n" \
                     f"|{pt_time:%I:%M%p}|{mt_time:%I:%M%p}|{ct_time:%I:%M%p}|{et_time:%I:%M%p}|{at_time:%I:%M%p}|"
        return time_table

    def construct_venue_table():
        venue_table = f"##Location\n" \
                      f"|Venue|\n" \
                      f"|:--:|\n" \
                      f"|**{game_info['venue']['name']}**|"

        return venue_table

    def construct_lineup_table():
        lineup_table = f"##Projected Lineups\n" \
                       f"*lines combos scraped from Daily Faceoff and may not be 100% accurate*\n\n" \
                       f"###Forwards\n\n" \
                       f"||LW|C|RW||LW|C|RW|\n" \
                       f"|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n"

        for (away_line, away_players), (home_line, home_players) in \
                zip(away_team_lineup['forwards'].items(), home_team_linup['forwards'].items()):
            lineup_table += f"|[]({teams[away_team_info['abbreviation']][0]})|" \
                            f"{away_players[0]}|" \
                            f"{away_players[1]}|" \
                            f"{away_players[2]}|" \
                            f"[]({teams[home_team_info['abbreviation']][0]})|" \
                            f"{home_players[0]}|" \
                            f"{home_players[1]}|" \
                            f"{home_players[2]}|\n"

        lineup_table += "###Defensemen\n\n" \
                        f"||LD|RD||LD|RD|\n" \
                        f"|:--:|:--:|:--:|:--:|:--:|:--:|\n"

        for (away_line, away_players), (home_line, home_players) in \
                zip(away_team_lineup['defense'].items(), home_team_linup['defense'].items()):
            lineup_table += f"|[]({teams[away_team_info['abbreviation']][0]})|" \
                            f"{away_players[0]}|" \
                            f"{away_players[1]}|" \
                            f"[]({teams[home_team_info['abbreviation']][0]})|" \
                            f"{home_players[0]}|" \
                            f"{home_players[1]}|\n"

        lineup_table += "###Goalies\n\n" \
                        f"||Starter|Backup||Starter|Backup|\n" \
                        f"|:--:|:--:|:--:|:--:|:--:|:--:|\n"

        for (away_line, away_players), (home_line, home_players) in \
                zip(away_team_lineup['goalie_list'].items(), home_team_linup['goalie_list'].items()):
            lineup_table += f"|[]({teams[away_team_info['abbreviation']][0]})|" \
                            f"{away_players[0]}|" \
                            f"{away_players[1]}|" \
                            f"[]({teams[home_team_info['abbreviation']][0]})|" \
                            f"{home_players[0]}|" \
                            f"{home_players[1]}|\n"

        return lineup_table

    def construct_injuries_table():
        injury_table = f"##Injuries\n" \
                       f"||Player|Date|Status|Details|\n" \
                       f"|:--:|:--:|:--:|:--:|:--:|\n"

        for player in away_team_injuries:
            injury_table += f"|[]({teams[away_team_info['abbreviation']][0]})|" \
                            f"{player['Player']}|" \
                            f"{player['Date']}|" \
                            f"{player['Status']}|" \
                            f"{player['Details']}|\n"

        injury_table += "|-|-|-|-|-|"
        for player in home_team_injuries:
            injury_table += f"|[]({teams[home_team_info['abbreviation']][0]})|" \
                            f"{player['Player']}|" \
                            f"{player['Date']}|" \
                            f"{player['Status']}|" \
                            f"{player['Details']}|\n"

        return injury_table

    def construct_sub_table():
        sub_table = f'##Subscribe\n' \
                    f'|Team Subreddits|\n' \
                    f'|:--:|:--:|\n' \
                    f"|{teams[away_team_info['abbreviation']][0]} {teams[home_team_info['abbreviation']][0]}\n" \
                    f'|[RedditHockey Discord](https://discord.gg/reddithockey)|'

        return sub_table

    def construct_notes():
        notes_table = f'##Thread Notes\n' \
                      f'* Trash talk is fun - but keep it civil\n' \
                      f'* Everything in this thread is automated and always a work in progress\n' \
                      f'* [Send me suggestions for improvements](https://www.reddit.com/user/airvvic/)'
        return notes_table

    # TODO Add Preseason Thread and Playoff Thread
    all_text.append(construct_title())
    all_text.append(construct_header())
    all_text.append(construct_split())
    all_text.append(construct_time_table())
    all_text.append(construct_venue_table())
    all_text.append(construct_lineup_table())
    all_text.append(construct_injuries_table())
    all_text.append(construct_split())
    all_text.append(construct_sub_table())
    all_text.append(construct_notes())
    save_markdown(all_text, 'gdt_markdown')
    return all_text


def post_gdt(markdown):
    try:
        submission = subreddit.submit(title=markdown.pop(0), selftext='\n'.join([section for section in markdown]),
                                      send_replies=False)
        print(f"Reddit thread successfully posted -> {submission.shortlink}")
        return submission
    except Exception as e:
        print(f"Couldn't submit post: {e}")
        return None


def comment_all_tables(submission, markdown):
    try:
        comment = submission.reply(body='\n'.join([section for section in markdown[2:-1] if "***" not in section]))
        print(f"Comment with tables successfully posted -> {comment.permalink}")
        return comment
    except Exception as e:
        print(f"Couldn't comment all tables: {e}")
        return None


def update_gdt_with_comment(submission, comment, markdown):
    try:
        markdown.insert(1, f'[comment with all tables]({comment.permalink})')
        submission = submission.edit(body='\n'.join([section for section in markdown]))
        print(f"Reddit thread updated with link to comment with all tables")
        return submission
    except Exception as e:
        print(f"Couldn't update post with comment to all tables: {e}")
        return None


def update_gdt(game):
    url = f"https://statsapi.web.nhl.com{game.game_info['link']}"
    w = requests.get(url)
    data = json.loads(w.content)
    w.close()

    period = data['liveData']['linescore']['currentPeriod']
    linescore = data['liveData']['linescore']
    _time = linescore.get('currentPeriodTimeRemaining')

    def create_time_clock():
        game.game_info['time'] = f'{ordinal} {_time}'
        print('Creating time table...')
        if _time == 'Final':
            time_table = '|Time Clock|\n|:--:|\n|FINAL|\n\n'
        else:
            time_table = f'|Time Clock|\n|:--:|\n|{ordinal} - {_time}|\n\n'
        return time_table

    def construct_boxscore():
        boxscore = '##Boxscore\n' \
                   '|Teams|1st|2nd|3rd|'
        if data['gameData']['game']['type'] in ['R', 'PR']:
            if period == 4:
                boxscore += 'OT|Total|\n|:--:|:--:|:--:|:--:|:--:|:--:|\n'
            elif period == 5:
                boxscore += 'OT|SO|Total|\n|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n'
            else:
                boxscore += 'Total|\n|:--:|:--:|:--:|:--:|:--:|\n'
        elif data['gameData']['game']['type'] == 'P':
            for x in range(0, (period - 3)):
                boxscore += f'OT{x + 1}|'
            boxscore += 'Total|\n|:--:|:--:|:--:|:--:|'
            for x in range(0, period - 3):
                boxscore += ':--:|'
            boxscore += ':--:|\n'
        home_total = data['liveData']['linescore']['teams']['home']['goals']
        away_total = data['liveData']['linescore']['teams']['away']['goals']
        score_dict = {}
        OT = 1
        for x in data['liveData']['linescore']['periods']:
            score = [x['away']['goals'], x['home']['goals']]
            if (data['gameData']['game']['type'] == 'P') and ('OT' in x['ordinalNum']) and (period > 4):
                score_dict['OT' + str(OT)] = score
                OT += 1
            else:
                score_dict[x['ordinalNum']] = score
        if period == 1:
            score_dict['2nd'] = ['--', '--']
            score_dict['3rd'] = ['--', '--']
        elif period == 2:
            score_dict['3rd'] = ['--', '--']
        if data['liveData']['linescore']['hasShootout']:
            awaySO = data['liveData']['linescore']['shootoutInfo']['away']['scores']
            homeSO = data['liveData']['linescore']['shootoutInfo']['home']['scores']
            if awaySO > homeSO:
                score_dict['SO'] = [1, 0]
            else:
                score_dict['SO'] = [0, 1]
        boxscore += f'|[]({away_team})|'
        for x in sorted(score_dict.keys()):
            boxscore += '{0}|'.format(score_dict[x][0])
        boxscore += f'{away_total}|\n|[]({home_team})|'
        for x in sorted(score_dict.keys()):
            boxscore += f'{score_dict[x][1]}|'
        boxscore += f'{home_total}|\n\n'
        return boxscore

    def construct_goal_table():
        allPlays = data['liveData']['plays']['allPlays']
        scoringPlays = data['liveData']['plays']['scoringPlays']
        goalDict = {'1st': [], '2nd': [], '3rd': [], 'OT': []}
        if (data['gameData']['game']['type'] in ['R', 'PR']) and (period == 5):
            goalDict['SO'] = []
        if (data['gameData']['game']['type'] == 'P') and (period > 4):
            del goalDict['OT']
            for x in range(0, (period - 4)):
                goalDict['OT' + str(x + 1)] = []
        OT = 1
        for x in scoringPlays:
            goal = allPlays[x]
            if (data['gameData']['game']['type'] == 'P') and ('OT' in goal['about']['ordinalNum']) and (
                    period > 4):
                goalDict['OT' + str(OT)].append([goal['about']['periodTime'], teams[
                    convert[goal['team']['name'].replace(u'\xe9', 'e').replace('.', '')]][0],
                                                 goal['result']['strength']['name'],
                                                 goal['result']['description'].replace(u'\xe9', 'e')])
                OT += 1
            else:
                goalDict[goal['about']['ordinalNum']].append([goal['about']['periodTime'], teams[
                    convert[goal['team']['name'].replace(u'\xe9', 'e').replace('.', '')]][0],
                                                              goal['result']['strength']['name'],
                                                              goal['result']['description'].replace(u'\xe9',
                                                                                                    'e')])
        goalTable = '##Goals\n' \
                    '|Period|Time|Team|Strength|Description|\n' \
                    '|:--:|:--:|:--:|:--:|:--:|\n'
        # Reverse for GDT and forward for PGT
        for x in sorted(goalDict.keys(), reverse=True):
            for y in goalDict[x][::-1]:
                if x == 'SO':
                    goalTable += f'|{x}|{y[0]}|[]({y[1]})|---|{y[3]}|\n'
                else:
                    goalTable += f'|{x}|{y[0]}|[]({y[1]})|{y[2]}|{y[3]}|\n'
        goalTable += '\n\n'
        return allPlays, goalTable

    def construct_team_stats():
        homeStats = data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']
        awayStats = data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']
        teamStats = '##Team Stats\n' \
                    '|Team|Shots|Hits|Blocked|FO Wins|Giveaways|Takeaways|Power Plays|\n' \
                    '|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n' \
                    f"|[]({away_team})|{awayStats['shots']}|{awayStats['hits']}|{awayStats['blocked']}" \
                    f"|{awayStats['faceOffWinPercentage']}%|{awayStats['giveaways']}" \
                    f"|{awayStats['takeaways']}|{str(int(awayStats['powerPlayGoals']))}" \
                    f"/{str(int(awayStats['powerPlayOpportunities']))}|\n" \
                    f"|[]({home_team})|{homeStats['shots']}|{homeStats['hits']}|{homeStats['blocked']}" \
                    f"|{homeStats['faceOffWinPercentage']}%|{homeStats['giveaways']}" \
                    f"|{homeStats['takeaways']}|{str(int(homeStats['powerPlayGoals']))}" \
                    f"/{str(int(homeStats['powerPlayOpportunities']))}|\n"
        return teamStats

    def construct_penalty_table():
        penalty_plays = data['liveData']['plays']['penaltyPlays']
        penalty_dict = {'1st': [], '2nd': [], '3rd': [], 'OT': []}
        if (data['gameData']['game']['type'] == 'P') and (period > 4):
            del penalty_dict['OT']
            for x in range(0, (period - 4)):
                penalty_dict['OT' + str(x + 1)] = []
        OT = 1
        for x in penalty_plays:
            penalty = all_plays[x]
            if (data['gameData']['game']['type'] == 'P') and ('OT' in penalty['about']['ordinalNum']) and (
                    period > 4):
                penalty_dict['OT' + str(OT)].append([penalty['about']['periodTime'], teams[
                    convert[penalty['team']['name'].replace(u'\xe9', 'e').replace('.', '')]][0],
                                                     penalty['result']['penaltySeverity'],
                                                     penalty['result']['penaltyMinutes'],
                                                     penalty['result']['description'].replace(u'\xe9', 'e')])
            else:
                penalty_dict[penalty['about']['ordinalNum']].append([penalty['about']['periodTime'], teams[
                    convert[penalty['team']['name'].replace(u'\xe9', 'e').replace('.', '')]][0],
                                                                     penalty['result']['penaltySeverity'],
                                                                     penalty['result']['penaltyMinutes'],
                                                                     penalty['result']['description'].replace(
                                                                         u'\xe9', 'e')])
        penalty_table = '##Penalties\n' \
                        '|Period|Time|Team|Type|Min|Description|\n' \
                        '|:--:|:--:|:-:|:--:|:--:|:--:|\n'
        # Reverse for GDT and forward for PGT
        for x in sorted(penalty_dict.keys(), reverse=True):
            for y in penalty_dict[x][::-1]:
                penalty_table += f'|{x}|{y[0]}|[]({y[1]})|{y[2]}|{y[3]}|{y[4]}|\n'
        penalty_table += '\n\n'
        return penalty_table

    def construct_highlights():
        game.get_game_content()
        game_content = game.game_content
        highlights = game_content['highlights']['scoreboard']['items']
        highlights_table = f'##Highlights\n'
        if highlights:
            highlights_table += f'||\n' \
                                f'|:--:|\n'
            for highlight in highlights:
                description = highlight['description']
                if description not in game.highlights:
                    playbacks = highlight['playbacks']
                    for item in playbacks:
                        if item['name'] == 'FLASH_1800K_896x504':
                            _url = item['url']
                            game.highlights[description] = _url
            for desc, link in game.highlights.items():
                highlights_table += f"|[{desc}]({link})|\n"
        else:
            highlights_table += f'|No Highlights|\n' \
                                f'|:--:|\n'
        return highlights_table

    if period == 0 or not _time:
        print('No updates')
    else:
        _time = data['liveData']['linescore']['currentPeriodTimeRemaining']
        ordinal = data['liveData']['linescore']['currentPeriodOrdinal']
        if f'{ordinal} {_time}' == game.game_info.get('time'):
            print('No updates')
        else:
            all_text = []
            all_text.append(construct_split())
            all_text.append(create_time_clock())
            home_team = teams[data['gameData']['teams']['home']['abbreviation']][0]
            away_team = teams[data['gameData']['teams']['away']['abbreviation']][0]
            print('Creating boxscore...')
            all_text.append(construct_boxscore())
            # Team Stats
            print('Creating team stats...')
            all_text.append(construct_team_stats())
            # Goals
            print('Creating goal table...')
            all_plays, goal_table = (construct_goal_table())
            all_text.append(goal_table)
            # Penalties
            print('Creating penalty table...')
            all_text.append(construct_penalty_table())
            # Highlights
            print('Creating highlights table')
            all_text.append(construct_highlights())
            # Produce second split
            all_text.append(construct_split())
            # Save markdown
            save_markdown(all_text, 'last_update_markdown')
            now = datetime.now()
            print(now.strftime('%I:%M%p') + ' - Updating thread...')
            op = game.gdt_post.selftext.split('***')
            game.gdt_post = game.gdt_post.edit(html.unescape(op[0] +
                                                             '\n'.join([section for section in all_text]) +
                                                             op[2]))

        if _time == 'Final':
            game.final = True
            return
        else:
            print('Sleeping...\n\n')
            return





