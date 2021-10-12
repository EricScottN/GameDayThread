from datetime import datetime, timedelta
import time
import pytz

utc = pytz.timezone('UTC')
eastern = pytz.timezone('US/Eastern')

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
        return False
    while gametime_ordinal > pretime:
        min, sec = divmod((gametime_ordinal - pretime).seconds, 60)
        hour, min = divmod(min, 60)
        print(f'Sleeping for {hour} hours {min} minutes until able to post')
        time.sleep((gametime_ordinal - pretime).seconds)
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
    header = f"#{away_team_info['name']} []({teams[away_team_info['abbreviation']][0]})" \
             f"({away_team_stats[0]['splits'][0]['stat']['wins']}-" \
             f"{away_team_stats[0]['splits'][0]['stat']['losses']}-" \
             f"{away_team_stats[0]['splits'][0]['stat']['ot']}) at " \
             f"{home_team_info['name']} []({teams[home_team_info['abbreviation']][0]})" \
             f"({home_team_stats[0]['splits'][0]['stat']['wins']}-" \
             f"{home_team_stats[0]['splits'][0]['stat']['losses']}-" \
             f"{home_team_stats[0]['splits'][0]['stat']['ot']})" \

    time = datetime.fromisoformat(game_info['gameDate'][:-1])
    utc_time = pytz.utc.localize(time, is_dst=None)
    at_time = utc_time.astimezone(pytz.timezone('Canada/Atlantic'))
    et_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
    ct_time = utc_time.astimezone(pytz.timezone("US/Central"))
    mt_time = utc_time.astimezone(pytz.timezone('US/Mountain'))
    pt_time = utc_time.astimezone(pytz.timezone('US/Pacific'))

    time_table = f"##Time\n" \
                 f"|PT|MT|CT|ET|AT|\n" \
                 f"|:--:|:--:|:--:|:--:|:--:|\n" \
                 f"|{pt_time:%I:%M%p}|{mt_time:%I:%M%p}|{ct_time:%I:%M%p}|{et_time:%I:%M%p}|{at_time:%I:%M%p}|"

    venue_table = f"##Location\n" \
                  f"|Venue|\n" \
                  f"|:--:|\n" \
                  f"|**{game_info['venue']['name']}**|"

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
                        f"{home_players[1]}|\n\n"

    injury_table = f"##Injuries\n" \
                   f"||Player|Date|Status|Details|\n" \
                   f"|:--:|:--:|:--:|:--:|:--:|\n"

    for player in away_team_injuries:
        injury_table += f"|[]({teams[away_team_info['abbreviation']][0]})|" \
                        f"{player['Player']}|" \
                        f"{player['Date']}|" \
                        f"{player['Status']}|" \
                        f"{player['Details']}|\n" \

    injury_table += "|-|-|-|-|-|"

    for player in home_team_injuries:
        injury_table += f"|[]({teams[home_team_info['abbreviation']][0]})|" \
                        f"{player['Player']}|" \
                        f"{player['Date']}|" \
                        f"{player['Status']}|" \
                        f"{player['Details']}|\n" \

    all_text = [header, time_table, venue_table, lineup_table, injury_table]

    print("\n".join(all_text))
