from src.team import get_all_teams, TeamInfo
from src.game import get_today_games, GameInfo
from src.gdt_post import find_gdt, can_post, generate_markdown_for_gdt, update_gdt, post_gdt, comment_all_tables, \
                         update_gdt_with_comment
from src.setup import get_env, args
import time


def main():
    teams = get_all_teams()
    today_games = get_today_games()
    team = TeamInfo.get_team_by_abbv(get_env('MY_TEAM'), teams)
    game = GameInfo.create_with_games_and_team(today_games, team.team_info)
    game.gdt_post = find_gdt(team.team_info['name'])
    if not game.gdt_post:
        if args.post_override or can_post(game.game_info):
            [obj.convert_team_name_to_text() for obj in [game.away_team, game.home_team]]
            [obj.get_team_stats_by_team_id() for obj in [game.away_team, game.home_team]]
            [obj.scrape_lineups() for obj in [game.away_team, game.home_team]]
            [obj.scrape_injuries() for obj in [game.away_team, game.home_team]]
            game.get_game_content()
            markdown = generate_markdown_for_gdt(game)
            submission = post_gdt(markdown)
            if submission:
                game.gdt_post = submission
                comment = comment_all_tables(submission, markdown)
                if comment:
                    submission = update_gdt_with_comment(submission, comment, markdown)

    while not game.final:
        update_gdt(game)
        time.sleep(60)


if __name__ == '__main__':
    main()



