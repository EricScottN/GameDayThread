from datetime import datetime, timedelta
import time
import pytz

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
        return False
    while gametime_ordinal > pretime:
        min, sec = divmod((gametime_ordinal - pretime).seconds, 60)
        hour, min = divmod(min, 60)
        print(f'Sleeping for {hour} hours {min} minutes until able to post')
        time.sleep((gametime_ordinal - pretime).seconds)
    else:
        return True

