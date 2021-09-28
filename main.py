from src.team import get_all_teams, get_team
from src.game import get_today_games, get_game_by_team_id, game_info
from src.gdt_post import find_gdt, can_post
from src.setup import get_env


def main():
    teams = get_all_teams()
    today_games = get_today_games()
    my_team = get_team(teams, get_env('MY_TEAM'))
    game = get_game_by_team_id(today_games, my_team)
    if not game:
        print(f"No game today for {my_team['name']}")
        return
    gdt_post = find_gdt(my_team['name'], get_env('SUBREDDIT'))
    if not gdt_post and can_post(game):
        lineups, injuries = game_info(game)













if __name__ == '__main__':
    main()



