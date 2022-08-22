import os

import pandas as pd

from src import api, season, configuration
from src.data_migrations import data_migration_modern_wild


def get_balances(season_balances_data_file, seasons_played_array):
    current_season_data = api.get_current_season()

    if os.path.isfile(season_balances_data_file):
        # Season balances file found only pull new seasons
        season_balances_df = pd.read_csv(season_balances_data_file, index_col=[0])
        season_balances_df = data_migration_modern_wild(season_balances_df, season_balances_data_file)

        # Determine if new data needs to be pulled?
        if season_balances_df.season.max() != current_season_data['id'] - 1:
            # continue pull x season data
            # TODO do only the pull for the x number season needed now all is pulled
            balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="DEC"))
            balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="VOUCHER"))
            balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="CREDITS"))
            balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="SPS"))
            balance_history_merits_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="MERITS"))

            next_season = season_balances_df.season.max() + 1
            for season_id in range(next_season, current_season_data['id']):
                print("Get balances season: " + str(season_id))

                # add new season
                season_balances_df = pd.concat([season_balances_df,
                                                pd.DataFrame({'season': [season_id], 'player': [configuration.ACCOUNT_NAME]})],
                                               ignore_index=True)

                season_balances_df = add_balance_data_to_season_df(season_balances_df,
                                                                   balance_history_credits_df,
                                                                   balance_history_dec_df,
                                                                   balance_history_sps_df,
                                                                   balance_history_voucher_df,
                                                                   balance_history_merits_df,
                                                                   single_season_id=season_id)
        else:
            print("All balances data is already pulled and processed continue with the current data set")

    else:
        # Get ALL

        # Get all balances
        balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="DEC"))
        balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="VOUCHER"))
        balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="CREDITS"))
        balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="SPS"))
        balance_history_merits_df = pd.DataFrame(api.get_balance_history_for_token(configuration.ACCOUNT_NAME, token="MERITS"))

        # Copy season id's from wild (because this will contain the most data, wild exists first)
        season_balances_df = pd.DataFrame()
        season_balances_df['season'] = seasons_played_array.tolist()
        season_balances_df['player'] = configuration.ACCOUNT_NAME
        season_balances_df = add_balance_data_to_season_df(season_balances_df,
                                                           balance_history_credits_df,
                                                           balance_history_dec_df,
                                                           balance_history_sps_df,
                                                           balance_history_voucher_df,
                                                           balance_history_merits_df)
        # Write and store
    season_balances_df.to_csv(season_balances_data_file)

    return season_balances_df


def add_balance_data_to_season_df(season_df,
                                  balance_history_credits_df,
                                  balance_history_dec_df,
                                  balance_history_sps_df,
                                  balance_history_voucher_df,
                                  balance_history_merits_df,
                                  single_season_id=None):
    season_end_times = season.get_season_end_times(configuration.time_zone)

    curr_season = api.get_current_season()
    last_season_name_id = int(curr_season['name'].split(' ')[-1]) - 1
    last_season_id = int(curr_season['id']) - 1
    season_df = season_df.sort_values(ascending=False, by=['season'])
    season_df['season_name'] = season_df.apply(
        lambda row: 'Splinterlands Season ' + str(last_season_name_id - (last_season_id - row['season'])), axis=1)
    season_df['season_id'] = season_df.apply(lambda row: last_season_name_id - (last_season_id - row['season']), axis=1)

    if single_season_id:
        season_arr = [single_season_id]
    else:
        season_arr = season_df.season.values

    for season_id in season_arr:
        end_date = [season_end_time['date'] for season_end_time in season_end_times if
                    season_end_time["id"] == season_id][0]
        start_date = [season_end_time['date'] for season_end_time in season_end_times if
                      season_end_time["id"] == season_id - 1][0]

        new_end_date = [season_end_time['date'] for season_end_time in season_end_times if
                        season_end_time["id"] == season_id + 1][0]
        new_start_date = [season_end_time['date'] for season_end_time in season_end_times if
                          season_end_time["id"] == season_id][0]

        # Voucher add
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_voucher_df,
                                                         'claim_staking_rewards', column_prefix="voucher_")

        # SPS add
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_sps_df,
                                                         'claim_staking_rewards', column_prefix='sps_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_sps_df,
                                                         'token_award', column_prefix='sps_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_sps_df,
                                                         'tournament_prize', column_prefix='sps_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_sps_df,
                                                         'enter_tournament', column_prefix='sps_')

        # Credits add
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_credits_df,
                                                         'quest_rewards', column_prefix='credits_')
        # NOTE SEASON REWARDS are always in the time frame of the new season
        season_df = cumulate_specific_balance_for_season(new_start_date, new_start_date, season_df, season_id,
                                                         balance_history_credits_df,
                                                         'season_rewards', column_prefix='credits_')

        # DEC add
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'dec_reward')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'quest_rewards', column_prefix='dec_')
        # NOTE SEASON REWARDS are always in the time frame of the new season
        season_df = cumulate_specific_balance_for_season(new_start_date, new_end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'season_rewards', column_prefix='dec_')

        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'tournament_prize', column_prefix='dec_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'enter_tournament', column_prefix='dec_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'rental_payment_fees', column_prefix='dec_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'rental_payment', column_prefix='dec_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'market_rental', column_prefix='dec_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'rental_refund', column_prefix='dec_')
        buy_df = balance_history_dec_df[(balance_history_dec_df.type == 'market_purchase') & (
                pd.to_numeric(balance_history_dec_df.amount) < 0)].copy()
        sell_df = balance_history_dec_df[(balance_history_dec_df.type == 'market_purchase') & (
                pd.to_numeric(balance_history_dec_df.amount) > 0)].copy()
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, buy_df,
                                                         'market_purchase',
                                                         column_prefix='dec_buy_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, sell_df,
                                                         'market_purchase',
                                                         column_prefix='dec_sell_')

        # MERITS add
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_merits_df,
                                                         'quest_rewards', column_prefix='merits_')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_merits_df,
                                                         'brawl_prize', column_prefix='merits_')
        # NOTE SEASON REWARDS are always in the time frame of the new season
        season_df = cumulate_specific_balance_for_season(new_start_date, new_end_date, season_df, season_id,
                                                         balance_history_merits_df,
                                                         'season_rewards', column_prefix='merits_')
    return season_df

def cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, input_df, search_type,
                                         column_prefix=""):
    # make sure it is a datetime field
    if not input_df.empty:
        input_df.created_date = pd.to_datetime(input_df.created_date)
        input_df.amount = pd.to_numeric(input_df.amount)

        # greater than the start date and smaller than the end date and type is search_type
        mask = (input_df['created_date'] > start_date) & (input_df['created_date'] <= end_date) & (
                input_df['type'] == search_type)

        # print("Amount " + str(search_type) + ": " + str(input_df.loc[mask].amount.sum()))
        season_df.loc[season_df.season == season_id, str(column_prefix + search_type)] = input_df.loc[mask].amount.sum()
    else:
        season_df.loc[season_df.season == season_id, str(column_prefix + search_type)] = 0
    return season_df
