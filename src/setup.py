import os
import argparse
import praw
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--title", type=str, help='append message to gdt title')
parser.add_argument("-po", "--post_override", type=bool, default=False)
parser.add_argument("-s", "--subreddit", type=str)
args = parser.parse_args()


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
