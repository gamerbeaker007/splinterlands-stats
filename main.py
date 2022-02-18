import os

from src import api, season, plots, hive_blog
import pandas as pd

from src.static_values_enum import Leagues, Edition

ACCOUNT_NAME = "beaker007"
# ACCOUNT_NAME = "bulldog1205"

USE_LOCAL_FILES = True
WRITE_TO_LOCAL_FILES = False


output_dir = os.path.join('output', ACCOUNT_NAME)
season_data_file = os.path.join(output_dir, 'season_data.csv')
balance_history_dec_data_file = os.path.join(output_dir, 'balance_history_dec_df.csv')
balance_history_voucher_data_file = os.path.join(output_dir, 'balance_history_voucher_df.csv')
balance_history_credits_data_file = os.path.join(output_dir, 'balance_history_credits_df.csv')
balance_history_sps_data_file = os.path.join(output_dir, 'balance_history_sps_df.csv')


def main():
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if os.path.isfile(season_data_file):
        season_df = pd.read_csv(season_data_file)
    else:
        season_df = pd.DataFrame(season.get_season_data(ACCOUNT_NAME))

    current_season_data = api.get_current_season()


    # # Determine if new data needs to be pulled?
    # if season_df.season.max() != current_season_data['id']-1:
    #     # continue pull x season data
    #
    # else:
    #     print("No new data found. continue creating blog with old data")


    balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="DEC"))
    balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="VOUCHER"))
    balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="CREDITS"))
    balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="SPS"))

    add_data_to_season_df(season_df, balance_history_credits_df, balance_history_dec_df, balance_history_sps_df,
                                             balance_history_voucher_df)

    plots.plot_season_stats_rating(season_df)
    plots.plot_season_stats_battles(season_df)
    plots.plot_season_stats_league(season_df)
    plots.plot_season_stats_earnings(season_df)


    # get last season market purchases
    season_end_times = season.get_season_end_times()
    end_date = [season_end_time['date'] for season_end_time in season_end_times if season_end_time["id"] == season_df.season.max()][0]
    start_date = [season_end_time['date'] for season_end_time in season_end_times if season_end_time["id"] == season_df.season.max() - 1][0]

    last_season_market_history = get_last_season_market_history(end_date, start_date)

    hive_blog.print_season_post(ACCOUNT_NAME, season_df, last_season_market_history)

    # Write and store
    season_df.to_csv(season_data_file)
    balance_history_dec_df.to_csv(balance_history_dec_data_file)
    balance_history_voucher_df.to_csv(balance_history_voucher_data_file)
    balance_history_credits_df.to_csv(balance_history_credits_data_file)
    balance_history_sps_df.to_csv(balance_history_sps_data_file)

    print("")


def get_last_season_market_history(end_date, start_date):
    market_history_df = pd.DataFrame(api.get_market_history(ACCOUNT_NAME))
    market_history_df['created_date'] = pd.to_datetime(market_history_df['created_date'])
    mask = (market_history_df['created_date'] > start_date) & (market_history_df['created_date'] <= end_date)
    last_season_market_history = market_history_df.loc[mask].copy()
    # Todo create card image name based on id/gold/xp/edition for each row
    card_details_list = api.get_card_details()
    last_season_market_history['edition_name'] = last_season_market_history.apply(
        lambda row: (Edition(row.edition)).name, axis=1)
    last_season_market_history['card_name'] = last_season_market_history.apply(
        lambda row: find_card_name(card_details_list, row.card_detail_id), axis=1)
    # combine_rates, combine_rates_gold, core_editions = api.get_combine_rates()
    # determine_card_level(combine_rates, core_editions, 3, 14)
    return last_season_market_history


def add_data_to_season_df(season_df, balance_history_credits_df, balance_history_dec_df, balance_history_sps_df,
                          balance_history_voucher_df):
    season_end_times = season.get_season_end_times()

    season_df['league_name'] = season_df.apply(lambda row: Leagues(row.league).name, axis=1)
    season_df['max_league_name'] = season_df.apply(lambda row: Leagues(row.max_league).name, axis=1)
    season_df['win_pct'] = season_df.apply(lambda row: (row.wins / row.battles * 100), axis=1)

    curr_season = api.get_current_season()
    curr_season_id = int(curr_season['name'].split(' ')[-1]) - 1
    season_df['season_name'] = season_df.apply(lambda row: 'Splinterlands Season ' + str(curr_season_id - row.name),
                                               axis=1)
    season_df['season_id'] = season_df.apply(lambda row: curr_season_id - row.name, axis=1)
    for season_id in season_df.season.values:
        end_date = \
        [season_end_time['date'] for season_end_time in season_end_times if season_end_time["id"] == season_id][0]
        start_date = [season_end_time['date'] for season_end_time in season_end_times if
                      season_end_time["id"] == season_id - 1][0]

        # Voucher add
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_voucher_df,
                                             'voucher_drop')

        # SPS add
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_sps_df,
                                             'claim_staking_rewards', column_prefix='sps_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_sps_df,
                                             'token_award', column_prefix='sps_')

        # Credits add
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_credits_df,
                                             'quest_rewards', column_prefix='credits_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_credits_df,
                                             'season_rewards', column_prefix='credits_')

        # DEC add
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'dec_reward')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'quest_rewards', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'season_rewards', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'tournament_prize', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'enter_tournament', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'rental_payment_fees', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'rental_payment', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'market_rental', column_prefix='dec_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, balance_history_dec_df,
                                             'rental_refund', column_prefix='dec_')


        buy_df = balance_history_dec_df[(balance_history_dec_df.type == 'market_purchase') & (pd.to_numeric(balance_history_dec_df.amount) < 0)].copy()
        sell_df = balance_history_dec_df[(balance_history_dec_df.type == 'market_purchase') & (pd.to_numeric(balance_history_dec_df.amount) > 0)].copy()
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, buy_df, 'market_purchase',
                                             column_prefix='dec_buy_')
        cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, sell_df, 'market_purchase',
                                             column_prefix='dec_sell_')


def determine_card_level(combine_rates, core_editions, edition, xp):
    for core_edition in core_editions:
        if core_edition == edition:
            selected_edition = core_edition
            break
        if core_edition > edition:
            print("edition to far so -1 " + str(core_edition))
            break

    print(selected_edition)
    return


def find_card_name(card_details_list, id):
    return list(filter(lambda card_details_dict: card_details_dict['id'] == id, card_details_list))[0]['name']


def cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, input_df, search_type, column_prefix=""):
    # make sure it is a datetime field
    input_df.created_date = pd.to_datetime(input_df.created_date)
    input_df.amount = pd.to_numeric(input_df.amount)

    # greater than the start date and smaller than the end date and type is search_type
    mask = (input_df['created_date'] > start_date) & (input_df['created_date'] <= end_date) & (input_df['type'] == search_type)

    # print("Amount " + str(search_type) + ": " + str(input_df.loc[mask].amount.sum()))
    season_df.loc[season_df.season == season_id, str(column_prefix + search_type)] = input_df.loc[mask].amount.sum()


if __name__ == '__main__':
    main()
