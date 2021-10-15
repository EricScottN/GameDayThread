import os
import argparse
import praw
from dotenv import load_dotenv


load_dotenv()


def get_env(var):
    result = os.getenv(var, None)
    return result


def check_team_length(team):
    if len(team) != 3:
        raise argparse.ArgumentTypeError('Team abbreviation must be three characters')
    return team


parser = argparse.ArgumentParser()
parser.add_argument("-po", "--post_override", type=bool, default=False,
                    help='Forces script to create post if team is found')
parser.add_argument("-so", "--subreddit", type=str, default=get_env('SUBREDDIT'),
                    help='Override subreddit - defaults to SUBREDDIT in .env file')
parser.add_argument("-to", "--team_override", type=check_team_length, default=get_env('MY_TEAM'),
                    help='Override team selection - defaults to MY_TEAM in .env file')
parser.add_argument("-tl", "--title", type=str,
                    help='Append a message to gdt reddit post title')

args = parser.parse_args()

def check_team_length(team):
    if len(team) != 3:
        raise argparse.ArgumentTypeError('Team abbreviation must be three characters')
    return team



class Reddit:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.username = os.getenv('R_USERNAME')
        self.password = os.getenv('R_PASSWORD')
        self.reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret,
                                  password=self.password, user_agent='Updating game thread',
                                  username=self.username)

def get_env(var):
    result = os.getenv(var, None)
    return result
