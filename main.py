from src.team import get_all_teams, TeamInfo
from src.game import get_today_games, get_game_by_team_id, GameInfo
from src.gdt_post import find_gdt, can_post, generate_markdown_for_gdt, update_gdt
from src.setup import get_env
import time


def main():
    teams = get_all_teams()
    today_games = get_today_games()
    team = TeamInfo.get_team_by_abbv(get_env('MY_TEAM'), teams)
    gdt_post = find_gdt(team.team_info['name'], get_env('SUBREDDIT'))
    game = GameInfo.create_with_games_and_team(today_games, team.team_info)
    if not gdt_post:
        #if can_post(game.game_info):
        [obj.convert_team_name_to_text() for obj in [game.away_team, game.home_team]]
        [obj.get_team_stats_by_team_id() for obj in [game.away_team, game.home_team]]
        [obj.scrape_lineups() for obj in [game.away_team, game.home_team]]
        [obj.scrape_injuries() for obj in [game.away_team, game.home_team]]
        game.get_game_content()
        markdown = generate_markdown_for_gdt(game)

    while not game.final:
        update_gdt(game)
        time.sleep(60)
    #Update the thread














if __name__ == '__main__':
    main()



