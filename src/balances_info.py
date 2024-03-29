import os

import numpy as np
import pandas as pd
from dateutil import parser

from src import api


def get_balances(account_name, season_balances_data_file):
    current_season_data = api.get_current_season()

    if os.path.isfile(season_balances_data_file):
        # Season balances file found only pull new seasons
        season_balances_df = pd.read_csv(season_balances_data_file, index_col=[0])

        # Determine if new data needs to be pulled?
        if season_balances_df.season.max() != current_season_data['id'] - 1:
            # continue pull x season data
            season_end_times = api.get_season_end_times()
            last_season_end_date = [season_end_time['date'] for season_end_time in season_end_times if
                                    season_end_time["id"] == season_balances_df.season.max()][0]

            balance_history_dec_df = pd.DataFrame(
                api.get_balance_history_for_token(account_name, token="DEC", from_date=last_season_end_date))
            balance_history_voucher_df = pd.DataFrame(
                api.get_balance_history_for_token(account_name, token="VOUCHER", from_date=last_season_end_date))
            balance_history_credits_df = pd.DataFrame(
                api.get_balance_history_for_token(account_name, token="CREDITS", from_date=last_season_end_date))
            balance_history_sps_df = pd.DataFrame(
                api.get_balance_history_for_token(account_name, token="SPS", from_date=last_season_end_date))
            balance_history_merits_df = pd.DataFrame(
                api.get_balance_history_for_token(account_name, token="MERITS", from_date=last_season_end_date))

            balance_history_sps_unclaimed_df = pd.DataFrame(
                api.get_balance_history_for_token(account_name, token="SPS", from_date=last_season_end_date,
                                                  unclaimed_sps=True))

            next_season = season_balances_df.season.max() + 1
            for season_id in range(next_season, current_season_data['id']):
                print("Get balances season: " + str(season_id))

                # add new season
                season_balances_df = pd.concat([season_balances_df,
                                                pd.DataFrame({'season': [season_id], 'player': [
                                                    account_name]})],
                                               ignore_index=True)

                season_balances_df = add_balance_data_to_season_df(season_balances_df,
                                                                   balance_history_credits_df,
                                                                   balance_history_dec_df,
                                                                   balance_history_sps_df,
                                                                   balance_history_voucher_df,
                                                                   balance_history_merits_df,
                                                                   balance_history_sps_unclaimed_df,
                                                                   season_array=[season_id])
        else:
            print("All balances data is already pulled and processed continue with the current data set")

    else:
        # Get ALL

        # Get all balances
        balance_history_dec_df = pd.DataFrame(
            api.get_balance_history_for_token(account_name, token="DEC"))
        balance_history_voucher_df = pd.DataFrame(
            api.get_balance_history_for_token(account_name, token="VOUCHER"))
        balance_history_credits_df = pd.DataFrame(
            api.get_balance_history_for_token(account_name, token="CREDITS"))
        balance_history_sps_df = pd.DataFrame(
            api.get_balance_history_for_token(account_name, token="SPS"))
        balance_history_merits_df = pd.DataFrame(
            api.get_balance_history_for_token(account_name, token="MERITS"))

        balance_history_sps_unclaimed_df = pd.DataFrame(
            api.get_balance_history_for_token(account_name, token="SPS", unclaimed_sps=True))

        current_season_data = api.get_current_season()
        first_season = determine_first_season_id_played(balance_history_dec_df, balance_history_sps_df)
        season_array = np.arange(first_season, current_season_data['id'])
        season_balances_df = pd.DataFrame()
        season_balances_df['season'] = season_array
        season_balances_df['player'] = account_name

        season_balances_df = add_balance_data_to_season_df(season_balances_df,
                                                           balance_history_credits_df,
                                                           balance_history_dec_df,
                                                           balance_history_sps_df,
                                                           balance_history_voucher_df,
                                                           balance_history_merits_df,
                                                           balance_history_sps_unclaimed_df,
                                                           season_array)
    # drop rows if all values in columns are NA remove
    number_of_columns = len(season_balances_df.columns.tolist())
    season_balances_df = season_balances_df.dropna(thresh=number_of_columns - 4)
    # Write and store
    season_balances_df.to_csv(season_balances_data_file)

    return season_balances_df


def add_balance_data_to_season_df(season_df,
                                  balance_history_credits_df,
                                  balance_history_dec_df,
                                  balance_history_sps_df,
                                  balance_history_voucher_df,
                                  balance_history_merits_df,
                                  balance_history_sps_unclaimed_df,
                                  season_array):
    season_end_times = api.get_season_end_times()

    curr_season = api.get_current_season()
    last_season_name_id = int(curr_season['name'].split(' ')[-1]) - 1
    last_season_id = int(curr_season['id']) - 1
    season_df = season_df.sort_values(ascending=False, by=['season'])
    season_df['season_name'] = season_df.apply(
        lambda row: 'Splinterlands Season ' + str(last_season_name_id - (last_season_id - row['season'])), axis=1)
    season_df['season_id'] = season_df.apply(lambda row: last_season_name_id - (last_season_id - row['season']), axis=1)

    for season_id in season_array:
        if season_id > season_end_times[0]['id']:
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
                                                             'token_transfer_multi', column_prefix='sps_')
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_df,
                                                             'enter_tournament', column_prefix='sps_')

            # SPS unclaimed add (earnings for quest/season/ranked battles)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'modern', column_prefix='sps_', unclaimed_reward=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'wild', column_prefix='sps_', unclaimed_reward=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'focus', column_prefix='sps_', unclaimed_reward=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'nightmare', column_prefix='sps_', unclaimed_reward=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'land', column_prefix='sps_', unclaimed_reward=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'brawl', column_prefix='sps_', unclaimed_reward=True)

            # NOTE SEASON REWARDS are always in the time frame of the new season
            season_df = cumulate_specific_balance_for_season(new_start_date, new_end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'season', column_prefix='sps_', unclaimed_reward=True, delegation=True)

            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'modern', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'wild', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'focus', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'nightmare', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'land', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'brawl', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)

            # NOTE SEASON REWARDS are always in the time frame of the new season
            season_df = cumulate_specific_balance_for_season(new_start_date, new_end_date, season_df, season_id,
                                                             balance_history_sps_unclaimed_df,
                                                             'season', column_prefix='sps_delegation_', unclaimed_reward=False, delegation=True)


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
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_dec_df,
                                                             'modern_leaderboard_prizes', column_prefix='dec_')
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_dec_df,
                                                             'leaderboard_prizes', column_prefix='dec_wild_')
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_dec_df,
                                                             'market_fees', column_prefix='dec_')
            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_dec_df,
                                                             'market_list_fee', column_prefix='dec_')

            season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                             balance_history_dec_df,
                                                             'purchased_energy', column_prefix='dec_')

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
        else:
            print("To old season '" + str(season_id) +
                  "' to process, do not have the season start and end times... sorry")
    return season_df


def cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id, input_df, search_type,
                                         column_prefix="", unclaimed_reward=False, delegation=False):
    # make sure it is a datetime field
    if not input_df.empty:
        input_df.created_date = pd.to_datetime(input_df.created_date)
        input_df.amount = pd.to_numeric(input_df.amount)

        # greater than the start date and smaller than the end date and type is search_type
        if unclaimed_reward:
            mask = (input_df['created_date'] > start_date) \
                   & (input_df['created_date'] <= end_date) \
                   & (input_df['type'] == search_type)\
                   & (input_df['amount'] < 0.0)\
                   & (input_df['to_player'] == season_df.player.iloc[0])
        elif delegation:
            mask = (input_df['created_date'] > start_date) \
                   & (input_df['created_date'] <= end_date) \
                   & (input_df['type'] == search_type) \
                   & (input_df['amount'] < 0.0) \
                   & (input_df['to_player'] != season_df.player.iloc[0])
        else:
            mask = (input_df['created_date'] > start_date) & (input_df['created_date'] <= end_date) & (
                    input_df['type'] == search_type)

        if search_type == "token_transfer_multi":
            mask = (input_df['created_date'] > start_date) \
                   & (input_df['created_date'] <= end_date) \
                   & (input_df['type'] == search_type) \
                   & (input_df['token'] == 'SPS')

        # print("Amount " + str(search_type) + ": " + str(input_df.loc[mask].amount.sum()))
        value = input_df.loc[mask].amount.sum()
        if unclaimed_reward and value < 0:
            value = value * -1
        season_df.loc[season_df.season == season_id, str(column_prefix + search_type)] = value
    else:
        season_df.loc[season_df.season == season_id, str(column_prefix + search_type)] = 0
    return season_df


def determine_first_season_id_played(balance_history_dec_df, balance_history_sps_df):
    first_earned_date_str = pd.concat([balance_history_dec_df, balance_history_sps_df]).created_date.sort_values().values[0]
    first_earned_date = parser.parse(first_earned_date_str)

    season_end_times = api.get_season_end_times()
    # determine which was the first season earning start
    for season_end_time in season_end_times:
        if first_earned_date <= season_end_time['date']:
            return season_end_time['id']
