import os
import pandas as pd
from src import api, season, plots, hive_blog, balances_info, configuration, battle_info, tournaments_info, market_info
from src.static_values_enum import Format

output_dir = os.path.join('output', configuration.ACCOUNT_NAME)
season_balances_data_file = os.path.join(output_dir, 'season_data.csv')
season_wild_battle_data_file = os.path.join(output_dir, 'season_wild_data.csv')
season_modern_battle_data_file = os.path.join(output_dir, 'season_modern_data.csv')


def main():
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    season_wild_df = battle_info.get_battle_info(season_wild_battle_data_file, Format.WILD)
    season_modern_df = battle_info.get_battle_info(season_modern_battle_data_file, Format.MODERN)

    # Determine season array of both wild and modern
    combined_season = pd.concat([season_wild_df, season_modern_df]).season.sort_values(ascending=False).unique().astype(int)
    season_balances_df = balances_info.get_balances(season_balances_data_file, combined_season)

    plots.plot_season_stats_rating(season_wild_df, output_dir, Format.WILD)
    plots.plot_season_stats_rating(season_modern_df, output_dir, Format.MODERN)
    plots.plot_season_stats_battles(season_wild_df, output_dir, Format.WILD)
    plots.plot_season_stats_battles(season_modern_df, output_dir, Format.MODERN)
    plots.plot_season_stats_earnings(season_balances_df, output_dir)

    # determine last season start and end time
    season_end_times = season.get_season_end_times(configuration.time_zone)
    end_date = [season_end_time['date'] for season_end_time in season_end_times if
                season_end_time["id"] == season_balances_df.season.max()][0]
    start_date = [season_end_time['date'] for season_end_time in season_end_times if
                  season_end_time["id"] == season_balances_df.season.max() - 1][0]

    # get tournament information
    tournaments_info_df = tournaments_info.get_tournaments_info(configuration.ACCOUNT_NAME, start_date, end_date)

    # get last season market purchases
    last_season_market_history = market_info.get_last_season_market_history(start_date, end_date)

    # get last season rewards
    current_season_data = api.get_current_season()
    last_season_player_history_rewards = market_info.get_last_season_player_history_rewards(start_date, end_date,
                                                                                current_season_data['id'] - 1)

    hive_blog.print_season_post(configuration.ACCOUNT_NAME,
                                season_balances_df,
                                season_wild_df,
                                season_modern_df,
                                last_season_market_history,
                                last_season_player_history_rewards,
                                tournaments_info_df,
                                output_dir)


if __name__ == '__main__':
    main()
