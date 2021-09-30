from src.team import get_all_teams, get_team, TeamInfo
from src.game import get_today_games, get_game_by_team_id, GameInfo
from src.gdt_post import find_gdt, can_post
from src.setup import get_env


def main():
    teams = get_all_teams()
    today_games = get_today_games()
    team = TeamInfo.get_my_team(get_env('MY_TEAM'), teams)
    game_data = GameInfo.create_with_today_games_and_team(today_games, team)
    # TODO get both teams info (away_team, home_team) and store them in instances of Team
    # TODO: get pregame data - Will need from:
    #           game: game_type, venue and address, datetime, gamecenter_link
    #           teams: records, radio_streams, preview, season_stats, subreddits
    #gdt_post = find_gdt(my_team['name'], get_env('SUBREDDIT'))
    #if not gdt_post and can_post(game):
        #lineups, injuries = game_info(game)













if __name__ == '__main__':
    main()



