import configparser
import json
import os
from datetime import datetime

import numpy as np
import pytz

from src import api, season, plots, hive_blog
import pandas as pd

from src.data_migrations import data_migration_modern_wild
from src.static_values_enum import Leagues, Edition, RatingLevel, Format

config = configparser.RawConfigParser()
config.read('config.properties')

time_zone = config.get('settings', 'time_zone')
ACCOUNT_NAME = config.get('settings', 'account_name')

output_dir = os.path.join('output', ACCOUNT_NAME)
season_balances_data_file = os.path.join(output_dir, 'season_data.csv')
season_wild_battle_data_file = os.path.join(output_dir, 'season_wild_data.csv')
season_modern_battle_data_file = os.path.join(output_dir, 'season_modern_data.csv')


def get_rating_from_ranked_battles(username, battle_history):
    df = pd.DataFrame()
    battle_history = battle_history.drop(battle_history[battle_history.match_type != "Ranked"].index)
    df['rating'] = battle_history.apply(lambda row: row.player_1_rating_final if row.player_1 == username else row.player_2_rating_final, axis=1)
    return df


def main():
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    current_season_data = api.get_current_season()
    if os.path.isfile(season_balances_data_file):
        season_balances_df = pd.read_csv(season_balances_data_file, index_col=[0])
        season_balances_df = data_migration_modern_wild(season_balances_df, season_balances_data_file)

        wild_all_done = False
        modern_all_done = False

        if os.path.isfile(season_wild_battle_data_file):
            season_wild_df = pd.read_csv(season_wild_battle_data_file, index_col=[0])
        else:
            season_wild_df = pd.DataFrame(season.get_all_season_data(ACCOUNT_NAME, Format.WILD))
            season_wild_df = add_battle_data_to_seasons_df(season_wild_df)
            season_wild_df.to_csv(season_wild_battle_data_file)
            wild_all_done = True

        if os.path.isfile(season_modern_battle_data_file):
            season_modern_df = pd.read_csv(season_modern_battle_data_file, index_col=[0])
        else:
            season_modern_df = pd.DataFrame(season.get_all_season_data(ACCOUNT_NAME, Format.MODERN))
            season_modern_df = add_battle_data_to_seasons_df(season_modern_df)
            season_modern_df.to_csv(season_modern_battle_data_file)
            modern_all_done = True

        # Determine if new data needs to be pulled?
        if season_balances_df.season.max() != current_season_data['id'] - 1:
            # continue pull x season data
            # TODO do only the pull for the x number season needed now all is pulled
            balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="DEC"))
            balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="VOUCHER"))
            balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="CREDITS"))
            balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="SPS"))
            balance_history_merits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="MERITS"))

            next_season = season_balances_df.season.max() + 1
            for season_id in range(next_season, current_season_data['id']):
                print("Get season data: " + str(season_id))
                if not wild_all_done and season_id not in season_wild_df.season.values:
                    season_wild_df_new = pd.DataFrame(api.get_leaderboard_with_player_season(ACCOUNT_NAME, season_id, mode=Format.WILD), index=[0])
                    season_wild_df_new = add_battle_data_to_seasons_df(season_wild_df_new)
                    season_wild_df = pd.concat([season_wild_df, season_wild_df_new], ignore_index=True)
                    season_wild_df.to_csv(season_wild_battle_data_file)

                if not modern_all_done and season_id not in season_modern_df.season.values:
                    season_modern_df_new = pd.DataFrame(api.get_leaderboard_with_player_season(ACCOUNT_NAME, season_id, mode=Format.MODERN), index=[0])
                    season_modern_df_new = add_battle_data_to_seasons_df(season_modern_df_new)
                    season_modern_df = pd.concat([season_modern_df, season_modern_df_new], ignore_index=True)
                    season_modern_df.to_csv(season_modern_battle_data_file)

                season_balances_df_new = season_wild_df[['season', 'player']].copy()
                season_balances_df = pd.concat([season_balances_df, pd.DataFrame(season_balances_df_new, index=[0])], ignore_index=True)

                season_balances_df = add_balance_data_to_season_df(season_balances_df,
                                                                   balance_history_credits_df,
                                                                   balance_history_dec_df,
                                                                   balance_history_sps_df,
                                                                   balance_history_voucher_df,
                                                                   balance_history_merits_df,
                                                                   single_season_id=season_id)
        else:
            print("All season data is already pulled and processed continue with the current data")
    else:
        # Get wild season leaderboard results
        season_wild_df = pd.DataFrame(season.get_all_season_data(ACCOUNT_NAME, Format.WILD))
        season_wild_df = add_battle_data_to_seasons_df(season_wild_df)
        season_wild_df.to_csv(season_wild_battle_data_file)

        # Get modern season leaderboard results
        season_modern_df = pd.DataFrame(season.get_all_season_data(ACCOUNT_NAME, Format.MODERN))
        season_modern_df = add_battle_data_to_seasons_df(season_modern_df)
        season_modern_df.to_csv(season_modern_battle_data_file)

        # Get all balances
        balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="DEC"))
        balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="VOUCHER"))
        balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="CREDITS"))
        balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="SPS"))
        balance_history_merits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="MERITS"))

        # Copy season id's from wild (because this will contain the most data, wild exists first)
        season_balances_df = season_wild_df[['season', 'player']].copy()
        season_balances_df = add_balance_data_to_season_df(season_balances_df,
                                                           balance_history_credits_df,
                                                           balance_history_dec_df,
                                                           balance_history_sps_df,
                                                           balance_history_voucher_df,
                                                           balance_history_merits_df)
    # Write and store
    season_balances_df.to_csv(season_balances_data_file)

    nr_of_battles = season_modern_df[season_modern_df.season == season_modern_df.season.max()].battles.values[0]
    battle_history_modern = pd.DataFrame(api.get_battle_history(ACCOUNT_NAME, nr_of_battles, Format.MODERN))
    nr_of_battles = season_wild_df[season_wild_df.season == season_wild_df.season.max()].battles.values[0]
    battle_history_wild = pd.DataFrame(api.get_battle_history(ACCOUNT_NAME, nr_of_battles, Format.WILD))

    plots.plot_season_stats_rating(season_wild_df, output_dir, Format.WILD)
    plots.plot_season_stats_rating(season_modern_df, output_dir, Format.MODERN)
    plots.plot_season_stats_battles(season_wild_df, output_dir, Format.WILD)
    plots.plot_season_stats_battles(season_modern_df, output_dir, Format.MODERN)
    plots.plot_season_stats_earnings(season_balances_df, output_dir)

    filtered_wild = get_rating_from_ranked_battles(ACCOUNT_NAME, battle_history_wild)
    filtered_modern = get_rating_from_ranked_battles(ACCOUNT_NAME, battle_history_modern)
    plots.plot_season_battle_history(filtered_wild, output_dir, Format.WILD)
    plots.plot_season_battle_history(filtered_modern, output_dir, Format.MODERN)


    # determine last season start and end time
    season_end_times = season.get_season_end_times(time_zone)
    end_date = [season_end_time['date'] for season_end_time in season_end_times if
                season_end_time["id"] == season_balances_df.season.max()][0]
    start_date = [season_end_time['date'] for season_end_time in season_end_times if
                  season_end_time["id"] == season_balances_df.season.max() - 1][0]

    # get tournament information
    tournaments_info_df = get_tournaments_info(ACCOUNT_NAME, start_date, end_date)

    # get last season market purchases
    last_season_market_history = get_last_season_market_history(start_date, end_date)

    # get last season rewards
    last_season_player_history_rewards = get_last_season_player_history_rewards(start_date, end_date,
                                                                                current_season_data['id'] - 1)

    hive_blog.print_season_post(ACCOUNT_NAME,
                                season_balances_df,
                                season_wild_df,
                                season_modern_df,
                                last_season_market_history,
                                last_season_player_history_rewards,
                                tournaments_info_df,
                                output_dir)


def filterDataFrameLastSeason(start_date, end_date, data_frame):
    # make sure created_date is of type time date
    date_field = 'created_date'
    data_frame[date_field] = pd.to_datetime(data_frame[date_field])

    # create mask, filter all date between season start and season end date
    mask = (data_frame[date_field] > start_date) & (data_frame[date_field] <= end_date)
    return data_frame.loc[mask].copy()


def get_last_season_market_history(start_date, end_date):
    market_history_df = pd.DataFrame(api.get_market_history(ACCOUNT_NAME))
    if not market_history_df.empty:
        last_season_market_history = filterDataFrameLastSeason(start_date, end_date, market_history_df)
        if not last_season_market_history.empty:
            # Todo create card image name based on id/gold/xp/edition for each row
            card_details_list = api.get_card_details()
            last_season_market_history['edition_name'] = last_season_market_history.apply(
                lambda row: (Edition(row.edition)).name, axis=1)
            last_season_market_history['card_name'] = last_season_market_history.apply(
                lambda row: find_card_name(card_details_list, row.card_detail_id), axis=1)
            # combine_rates, combine_rates_gold, core_editions = api.get_combine_rates()
            # determine_card_level(combine_rates, core_editions, 3, 14)
        return last_season_market_history
    else:
        return market_history_df


def get_last_season_player_history_rewards(start_date, end_date, season_id):
    player_history_df = pd.DataFrame(api.get_player_history_rewards(ACCOUNT_NAME))
    reward_data = pd.DataFrame()

    # Find season reward
    for index, row in player_history_df.iterrows():
        data = json.loads(row.data)
        if row.success and data['type'] == 'league_season' and data['season'] == season_id:
            reward_data = pd.concat([reward_data, pd.DataFrame(json.loads(row.result)['rewards'])], ignore_index=True)
            break

    last_season_player_history_rewards = filterDataFrameLastSeason(start_date, end_date, player_history_df)

    # Find all quest rewards
    for index, row in last_season_player_history_rewards.iterrows():
        data = json.loads(row.data)
        if row.success and data['type'] == 'quest':
            reward_data = pd.concat([reward_data, pd.DataFrame(json.loads(row.result)['rewards'])], ignore_index=True)

    # For all reward card subtract addition information
    reward_data['card_detail_id'] = reward_data.apply(
        lambda row: row.card['card_detail_id'] if row['type'] == 'reward_card' else "", axis=1)
    reward_data['xp'] = reward_data.apply(lambda row: row.card['xp'] if row['type'] == 'reward_card' else "", axis=1)
    reward_data['gold'] = reward_data.apply(lambda row: row.card['gold'] if row['type'] == 'reward_card' else "",
                                            axis=1)

    # Create column if it does not exist (only exists when packs where received)
    if 'edition' not in reward_data:
        reward_data['edition'] = np.nan

    reward_data['edition'] = reward_data.apply(
        lambda row: row.card['edition'] if row['type'] == 'reward_card' else row['edition'], axis=1)

    card_details_list = api.get_card_details()
    reward_data['edition_name'] = reward_data.apply(
        lambda row: (Edition(row.edition)).name if row['type'] == 'reward_card' else "", axis=1)
    reward_data['card_name'] = reward_data.apply(
        lambda row: find_card_name(card_details_list, row.card_detail_id) if row['type'] == 'reward_card' else "",
        axis=1)

    # combine_rates, combine_rates_gold, core_editions = api.get_combine_rates()
    # determine_card_level(combine_rates, core_editions, 3, 14)
    return reward_data


def add_battle_data_to_seasons_df(season_df):
    season_ratings = [0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 5100]

    if not season_df.empty:
        # translate end rating to max (for graph)
        season_df['end_league_rating'] = season_df.apply(lambda row: season_ratings[row.league], axis=1)

        season_df['league_name'] = season_df.apply(lambda row: Leagues(row.league).name, axis=1)

        # check if max_league is there for last season max league is not filled yet.

        season_df['max_league_name'] = season_df.apply(lambda row: Leagues(row.max_league).name, axis=1)
        season_df['win_pct'] = season_df.apply(lambda row: (row.wins / row.battles * 100), axis=1)

        curr_season = api.get_current_season()
        last_season_name_id = int(curr_season['name'].split(' ')[-1]) - 1
        last_season_id = int(curr_season['id']) - 1
        season_df = season_df.sort_values(ascending=False, by=['season'])
        season_df['season_name'] = season_df.apply(
            lambda row: 'Splinterlands Season ' + str(last_season_name_id - (last_season_id - row['season'])), axis=1)
        season_df['season_id'] = season_df.apply(lambda row: last_season_name_id - (last_season_id - row['season']), axis=1)

    return season_df


def add_balance_data_to_season_df(season_df,
                                  balance_history_credits_df,
                                  balance_history_dec_df,
                                  balance_history_sps_df,
                                  balance_history_voucher_df,
                                  balance_history_merits_df,
                                  single_season_id=None):
    season_end_times = season.get_season_end_times(time_zone)

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


def get_tournaments_info(username, start_date, end_date):
    collect = pd.DataFrame()
    tournaments_ids = api.get_player_tournaments_ids(username)
    for tournament_id in tournaments_ids:
        tournament = api.get_tournament(tournament_id)
        utc = pytz.UTC

        if tournament['status'] == 2 and tournament['rounds'][-1]['status'] == 2:
            date_time = utc.localize(
                datetime.strptime(tournament['rounds'][-1]['start_date'], "%Y-%m-%dT%H:%M:%S.000Z"))

            if start_date <= date_time <= end_date:
                player_data = list(filter(lambda item: item['player'] == username, tournament['players']))
                # If player did not leave and is found continue
                if player_data:
                    player_data = player_data[0]

                    prize = "0"
                    if player_data['prize']:
                        prize = player_data['prize']
                    else:
                        if player_data['ext_prize_info']:
                            prize_info = json.loads(player_data['ext_prize_info'])
                            prize = prize_info[0]['qty'] + " " + prize_info[0]['type']

                    tournament_record = {
                        'name': tournament['name'],
                        'league': RatingLevel(tournament['data']['rating_level']).name,
                        'num_players': tournament['num_players'],
                        'finish': player_data['finish'],
                        'wins': player_data['wins'],
                        'losses': player_data['losses'],
                        'draws': player_data['draws'],
                        'entry_fee': player_data['fee_amount'],
                        'prize': prize
                    }
                    collect = pd.concat([collect, pd.DataFrame(tournament_record, index=[0])], ignore_index=True)
    return collect


if __name__ == '__main__':
    main()
