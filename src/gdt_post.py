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

    # TODO Add Preseason Thread and Playoff Thread
    all_text.append(construct_title(away_team_info, away_team_stats, home_team_info, home_team_stats, home_team_time))
    all_text.append(construct_header(away_team_info, away_team_stats, home_team_info, home_team_stats))
    all_text.append(construct_split())
    all_text.append(construct_time_table(at_time, ct_time, et_time, mt_time, pt_time))
    all_text.append(construct_venue_table(game_info))
    all_text.append(construct_lineup_table(away_team_info, away_team_lineup, home_team_info, home_team_linup))
    all_text.append(construct_injuries_table(away_team_info, away_team_injuries, home_team_info, home_team_injuries))
    all_text.append(construct_split())
    all_text.append(construct_sub_table(away_team_info, home_team_info))
    all_text.append(construct_notes())

    textfile = open("gdt_post_markdown.txt", "w")
    for element in all_text:
        textfile.write(element + "\n")
    textfile.close()
    return all_text


def construct_title(away_team_info, away_team_stats, home_team_info, home_team_stats, home_team_time):
    title = f"Game Day Thread: " \
            f"{away_team_info['name']} " \
            f"({away_team_stats[0]['splits'][0]['stat']['wins']}-" \
            f"{away_team_stats[0]['splits'][0]['stat']['losses']}-" \
            f"{away_team_stats[0]['splits'][0]['stat']['ot']}) at " \
            f"{home_team_info['name']} " \
            f"({home_team_stats[0]['splits'][0]['stat']['wins']}-" \
            f"{home_team_stats[0]['splits'][0]['stat']['losses']}-" \
            f"{home_team_stats[0]['splits'][0]['stat']['ot']}) - " \
            f"{home_team_time:%d %b %Y - %I:%M%p} {home_team_info['venue']['timeZone']['tz']}"
    if args.title:
        title += f' - {args.title}'

    return title


def construct_header(away_team_info, away_team_stats, home_team_info, home_team_stats):
    header = f"#{away_team_info['name']} []({teams[away_team_info['abbreviation']][0]})" \
             f"({away_team_stats[0]['splits'][0]['stat']['wins']}-" \
             f"{away_team_stats[0]['splits'][0]['stat']['losses']}-" \
             f"{away_team_stats[0]['splits'][0]['stat']['ot']}) at " \
             f"{home_team_info['name']} []({teams[home_team_info['abbreviation']][0]})" \
             f"({home_team_stats[0]['splits'][0]['stat']['wins']}-" \
             f"{home_team_stats[0]['splits'][0]['stat']['losses']}-" \
             f"{home_team_stats[0]['splits'][0]['stat']['ot']})"

    return header


def construct_split():
    return f"\n***\n"


def construct_time_table(at_time, ct_time, et_time, mt_time, pt_time):
    time_table = f"##Time\n" \
                 f"|PT|MT|CT|ET|AT|\n" \
                 f"|:--:|:--:|:--:|:--:|:--:|\n" \
                 f"|{pt_time:%I:%M%p}|{mt_time:%I:%M%p}|{ct_time:%I:%M%p}|{et_time:%I:%M%p}|{at_time:%I:%M%p}|"
    return time_table


def construct_venue_table(game_info):
    venue_table = f"##Location\n" \
                  f"|Venue|\n" \
                  f"|:--:|\n" \
                  f"|**{game_info['venue']['name']}**|"

    return venue_table


def construct_lineup_table(away_team_info, away_team_lineup, home_team_info, home_team_linup):
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


def construct_injuries_table(away_team_info, away_team_injuries, home_team_info, home_team_injuries):
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


def construct_sub_table(away_team_info, home_team_info):
    sub_table = f'##Subscribe\n' \
                f'|Team Subreddits|\n' \
                f'|:--:|:--:|\n' \
                f"|{teams[away_team_info['abbreviation']][0]} {teams[home_team_info['abbreviation']][0]}\n" \
                f'|[RedditHockey Discord](https://discord.gg/reddithockey)|' \

    return sub_table


def construct_notes():
    notes_table = f'##Thread Notes\n' \
                  f'* Trash talk is fun - but keep it civil\n' \
                  f'* Everything in this thread is automated and always a work in progress\n' \
                  f'* [Send me suggestions for improvements](https://www.reddit.com/user/airvvic/)'
    return notes_table


def post_gdt(markdown):
    try:
        submission = subreddit.submit(title=markdown.pop(0), selftext='\n'.join([section for section in markdown]),
                                      send_replies=False)
        return submission
    except Exception as e:
        print(f"Couldn't submit post: {e}")
        return None


def comment_all_tables(submission, markdown):
    try:
        comment = submission.reply(body='\n'.join([section for section in markdown[2:-1] if "***" not in section]))
        return comment
    except Exception as e:
        print(f"Couldn't comment all tables: {e}")
        return None


def update_gdt_with_comment(submission, comment, markdown):
    try:
        markdown.insert(1, f'[comment with all tables]({comment.permalink})')
        submission = submission.edit(body='\n'.join([section for section in markdown]))
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
    time = linescore.get('currentPeriodTimeRemaining')
    if period == 0 or not time:
        print('No updates')
    else:
        time = data['liveData']['linescore']['currentPeriodTimeRemaining']
        ordinal = data['liveData']['linescore']['currentPeriodOrdinal']
        if f'{ordinal} {time}' == game.game_info.get('time'):
            print('No updates')
        else:
            game.game_info['time'] = f'{ordinal} {time}'
            print('Creating time table...')
            if time == 'Final':
                timeTable = '|Time Clock|\n|:--:|\n|FINAL|\n\n'
            else:
                timeTable = f'|Time Clock|\n|:--:|\n|{ordinal} - {time}|\n\n'

            homeTeam = teams[data['gameData']['teams']['home']['abbreviation']][0]
            awayTeam = teams[data['gameData']['teams']['away']['abbreviation']][0]

            print('Creating boxscore...')
            boxscore = '|Teams|1st|2nd|3rd|'

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

            homeTotal = data['liveData']['linescore']['teams']['home']['goals']
            awayTotal = data['liveData']['linescore']['teams']['away']['goals']
            scoreDict = {}

            OT = 1
            for x in data['liveData']['linescore']['periods']:
                score = [x['away']['goals'], x['home']['goals']]
                if (data['gameData']['game']['type'] == 'P') and ('OT' in x['ordinalNum']) and (period > 4):
                    scoreDict['OT' + str(OT)] = score
                    OT += 1
                else:
                    scoreDict[x['ordinalNum']] = score

            if period == 1:
                scoreDict['2nd'] = ['--', '--']
                scoreDict['3rd'] = ['--', '--']
            elif period == 2:
                scoreDict['3rd'] = ['--', '--']

            if data['liveData']['linescore']['hasShootout']:
                awaySO = data['liveData']['linescore']['shootoutInfo']['away']['scores']
                homeSO = data['liveData']['linescore']['shootoutInfo']['home']['scores']
                if awaySO > homeSO:
                    scoreDict['SO'] = [1, 0]
                else:
                    scoreDict['SO'] = [0, 1]

            boxscore += f'|[]({awayTeam})|'
            for x in sorted(scoreDict.keys()):
                boxscore += '{0}|'.format(scoreDict[x][0])

            boxscore += f'{awayTotal}|\n|[]({homeTeam})|'
            for x in sorted(scoreDict.keys()):
                boxscore += f'{scoreDict[x][1]}|'

            boxscore += f'{homeTotal}|\n\n'

            # Team Stats
            print('Creating team stats...')
            homeStats = data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']
            awayStats = data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']
            teamStats = '|Team|Shots|Hits|Blocked|FO Wins|Giveaways|Takeaways|Power ' \
                        'Plays|\n|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n'
            teamStats += f"|[]({awayTeam})|{awayStats['shots']}|{awayStats['hits']}|{awayStats['blocked']}" \
                         f"|{awayStats['faceOffWinPercentage']}%|{awayStats['giveaways']}" \
                         f"|{awayStats['takeaways']}|{str(int(awayStats['powerPlayGoals']))}" \
                         f"/{str(int(awayStats['powerPlayOpportunities']))}|\n"

            teamStats += f"|[]({homeTeam})|{homeStats['shots']}|{homeStats['hits']}|{homeStats['blocked']}" \
                         f"|{homeStats['faceOffWinPercentage']}%|{homeStats['giveaways']}" \
                         f"|{homeStats['takeaways']}|{str(int(homeStats['powerPlayGoals']))}" \
                         f"/{str(int(homeStats['powerPlayOpportunities']))}|\n"

            # Goals
            print('Creating goal table...')
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

            goalTable = '|Period|Time|Team|Strength|Description|\n|:--:|:--:|:--:|:--:|:--:|\n'

            # Reverse for GDT and forward for PGT
            for x in sorted(goalDict.keys(), reverse=True):
                for y in goalDict[x][::-1]:
                    if x == 'SO':
                        goalTable += f'|{x}|{y[0]}|[]({y[1]})|---|{y[3]}|\n'
                    else:
                        goalTable += f'|{x}|{y[0]}|[]({y[1]})|{y[2]}|{y[3]}|\n'

            goalTable += '\n\n'

            # Penalties
            print('Creating penalty table...')
            penaltyPlays = data['liveData']['plays']['penaltyPlays']
            penaltyDict = {'1st': [], '2nd': [], '3rd': [], 'OT': []}

            if (data['gameData']['game']['type'] == 'P') and (period > 4):
                del penaltyDict['OT']
                for x in range(0, (period - 4)):
                    penaltyDict['OT' + str(x + 1)] = []

            OT = 1
            for x in penaltyPlays:
                penalty = allPlays[x]
                if (data['gameData']['game']['type'] == 'P') and ('OT' in penalty['about']['ordinalNum']) and (
                        period > 4):
                    penaltyDict['OT' + str(OT)].append([penalty['about']['periodTime'], teams[
                        convert[penalty['team']['name'].replace(u'\xe9', 'e').replace('.', '')]][0],
                                                        penalty['result']['penaltySeverity'],
                                                        penalty['result']['penaltyMinutes'],
                                                        penalty['result']['description'].replace(u'\xe9', 'e')])
                else:
                    penaltyDict[penalty['about']['ordinalNum']].append([penalty['about']['periodTime'], teams[
                        convert[penalty['team']['name'].replace(u'\xe9', 'e').replace('.', '')]][0],
                                                                        penalty['result']['penaltySeverity'],
                                                                        penalty['result']['penaltyMinutes'],
                                                                        penalty['result']['description'].replace(
                                                                            u'\xe9', 'e')])

            penaltyTable = '|Period|Time|Team|Type|Min|Description|\n|:--:|:--:|:-:|:--:|:--:|:--:|\n'
            # Reverse for GDT and forward for PGT
            for x in sorted(penaltyDict.keys(), reverse=True):
                for y in penaltyDict[x][::-1]:
                    penaltyTable += f'|{x}|{y[0]}|[]({y[1]})|{y[2]}|{y[3]}|{y[4]}|\n'

            penaltyTable += '\n\n'

            tables = f'***\n\n{timeTable}\n###Boxscore\n{boxscore}###Goals\n{goalTable}###Team Stats\n{teamStats}' \
                     f'###Penalties\n{penaltyTable}***'

            now = datetime.now()
            print(now.strftime('%I:%M%p') + ' - Updating thread...')
            op = game.gdt_post.selftext.split('***')
            game.gdt_post = game.gdt_post.edit(html.unescape(op[0] + tables + op[2]))

        if time == 'Final':
            game.final = True
            return
        else:
            print('Sleeping...\n\n')
            return
