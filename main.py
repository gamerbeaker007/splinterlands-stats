import os
import pandas as pd
from src import api, season, plots, hive_blog, balances_info, configuration, battle_info, tournaments_info, market_info
from src.static_values_enum import Format


def main():
    account_names_str = os.environ.get("ACCOUNT_NAMES")
    time_zone = os.environ.get("TIME_ZONE")
    skip_zeros = os.environ.get("SKIP_ZEROS")
    output_dir_base = 'output'

    if not account_names_str:
        print("No environment ACCOUNT_NAMES found, using default from config.properties")
        account_names_str = configuration.ACCOUNT_NAMES
    if not time_zone:
        print("No environment TIME_ZONE found, using default from config.properties")
        time_zone = configuration.TIME_ZONE
    if not skip_zeros:
        print("No environment SKIP_ZEROS found, using default from config.properties")
        skip_zeros = configuration.SKIP_ZEROS

    account_names = account_names_str.split(',')

    # Pre create dictionaries to store information
    season_wild_dict = {}
    season_modern_dict = {}
    season_balances_dict = {}
    tournaments_info_dict = {}
    purchases_dict = {}
    sold_dict = {}
    last_season_rewards_dict = {}
    start_date, end_date, previous_season_id = season.get_previous_season_dates_and_id(time_zone)

    for account_name in account_names:
        print("\n\nGetting information for account: " + str(account_name) +
              " with time zone: " + str(time_zone))
        output_dir_account = os.path.join(output_dir_base, account_name)
        season_balances_data_file = os.path.join(output_dir_account, 'season_data.csv')
        season_wild_battle_data_file = os.path.join(output_dir_account, 'season_wild_data.csv')
        season_modern_battle_data_file = os.path.join(output_dir_account, 'season_modern_data.csv')

        if not os.path.exists(output_dir_account):
            os.mkdir(output_dir_account)

        season_wild_dict[account_name] = battle_info.get_battle_info(account_name,
                                                                season_wild_battle_data_file,
                                                                Format.WILD)
        season_modern_dict[account_name] = battle_info.get_battle_info(account_name,
                                                                       season_modern_battle_data_file,
                                                                       Format.MODERN)

        # Determine season array of both wild and modern
        combined_season = pd.concat([season_wild_dict[account_name], season_modern_dict[account_name]])
        combined_season = combined_season.season.sort_values(ascending=False).unique().astype(int)
        season_balances_dict[account_name] = balances_info.get_balances(account_name,
                                                                        time_zone,
                                                                        season_balances_data_file,
                                                                        combined_season)

        plots.plot_season_stats_rating(season_wild_dict[account_name], output_dir_account, Format.WILD)
        plots.plot_season_stats_rating(season_modern_dict[account_name], output_dir_account, Format.MODERN)
        plots.plot_season_stats_battles(season_wild_dict[account_name], output_dir_account, Format.WILD)
        plots.plot_season_stats_battles(season_modern_dict[account_name], output_dir_account, Format.MODERN)

        plots.plot_season_stats_earnings(season_balances_dict[account_name], output_dir_account, skip_zeros=skip_zeros)

        print("Get tournament and market info for season " + str(previous_season_id) +
              " Start: " + str(start_date) +
              " End: " + str(end_date))

        # get tournament information
        tournaments_info_dict[account_name] = tournaments_info.get_tournaments_info(account_name, start_date, end_date)

        purchases_dict[account_name], sold_dict[account_name] = market_info.get_purchased_sold_cards(account_name,
                                                                                                     start_date,
                                                                                                     end_date)

        # get last season rewards
        last_season_rewards_dict[account_name] = market_info.get_last_season_player_history_rewards(account_name,
                                                                                                    start_date,
                                                                                                    end_date,
                                                                                                    previous_season_id)

        # print single post for each account
        hive_blog.write_blog_post([account_name],
                                  season_balances_dict,
                                  season_wild_dict,
                                  season_modern_dict,
                                  last_season_rewards_dict,
                                  tournaments_info_dict,
                                  purchases_dict,
                                  sold_dict,
                                  previous_season_id,
                                  skip_zeros,
                                  os.path.join(output_dir_account, "post.txt"))

    # If multiple account the also write a combined post
    if len(account_names) > 1:
        hive_blog.write_blog_post(account_names,
                                  season_balances_dict,
                                  season_wild_dict,
                                  season_modern_dict,
                                  last_season_rewards_dict,
                                  tournaments_info_dict,
                                  purchases_dict,
                                  sold_dict,
                                  previous_season_id,
                                  skip_zeros,
                                  os.path.join(output_dir_base, "combined_post.txt"))

    season.print_new_season_dates()


if __name__ == '__main__':
    main()
