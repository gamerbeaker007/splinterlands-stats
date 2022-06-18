import json
import os
from datetime import datetime

import numpy as np
import pytz

from src import api, season, plots, hive_blog
import pandas as pd

from src.static_values_enum import Leagues, Edition, RatingLevel

time_zone = 'Europe/Amsterdam'

ACCOUNT_NAME = "beaker007"
# ACCOUNT_NAME = "shinoumonk"

output_dir = os.path.join('output', ACCOUNT_NAME)
season_data_file = os.path.join(output_dir, 'season_data.csv')


def main():
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    current_season_data = api.get_current_season()
    if os.path.isfile(season_data_file):
        season_df = pd.read_csv(season_data_file, index_col=[0])
        # Determine if new data needs to be pulled?
        if season_df.season.max() != current_season_data['id'] - 1:
            # continue pull x season data
            balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="DEC"))
            balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="VOUCHER"))
            balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="CREDITS"))
            balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="SPS"))

            next_season = season_df.season.max() + 1
            for season_id in range(next_season, current_season_data['id']):
                print("Get season data: " + str(season_id))
                season_data = api.get_leaderboard_with_player_season(ACCOUNT_NAME, season_id)
                season_df = season_df.append(season_data, ignore_index=True)
                season_df = add_data_to_season_df(season_df,
                                                  balance_history_credits_df,
                                                  balance_history_dec_df,
                                                  balance_history_sps_df,
                                                  balance_history_voucher_df,
                                                  single_season_id=season_id)
        else:
            print("All season data is already pulled and processed continue with the current data")
    else:
        season_array = season.get_all_season_data(ACCOUNT_NAME)
        season_df = pd.DataFrame(season_array)
        balance_history_dec_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="DEC"))
        balance_history_voucher_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="VOUCHER"))
        balance_history_credits_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="CREDITS"))
        balance_history_sps_df = pd.DataFrame(api.get_balance_history_for_token(ACCOUNT_NAME, token="SPS"))
        season_df = add_data_to_season_df(season_df,
                                          balance_history_credits_df,
                                          balance_history_dec_df,
                                          balance_history_sps_df,
                                          balance_history_voucher_df)

    plots.plot_season_stats_rating(season_df, output_dir)
    plots.plot_season_stats_battles(season_df, output_dir)
    plots.plot_season_stats_earnings(season_df, output_dir)

    # determine last season start and end time
    season_end_times = season.get_season_end_times(time_zone)
    end_date = [season_end_time['date'] for season_end_time in season_end_times if
                season_end_time["id"] == season_df.season.max()][0]
    start_date = [season_end_time['date'] for season_end_time in season_end_times if
                  season_end_time["id"] == season_df.season.max() - 1][0]

    # get tournament information
    tournaments_info_df = get_tournaments_info(ACCOUNT_NAME, start_date, end_date)

    # get last season market purchases
    last_season_market_history = get_last_season_market_history(start_date, end_date)

    # get last season rewards
    last_season_player_history_rewards = get_last_season_player_history_rewards(start_date, end_date,
                                                                                current_season_data['id'] - 1)

    hive_blog.print_season_post(ACCOUNT_NAME,
                                season_df,
                                last_season_market_history,
                                last_season_player_history_rewards,
                                tournaments_info_df,
                                output_dir)

    # Write and store
    season_df.to_csv(season_data_file)


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
            reward_data = reward_data.append(pd.DataFrame(json.loads(row.result)['rewards']))
            break

    last_season_player_history_rewards = filterDataFrameLastSeason(start_date, end_date, player_history_df)

    # Find all quest rewards
    for index, row in last_season_player_history_rewards.iterrows():
        data = json.loads(row.data)
        if row.success and data['type'] == 'quest':
            reward_data = reward_data.append(pd.DataFrame(json.loads(row.result)['rewards']))

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


def add_data_to_season_df(season_df,
                          balance_history_credits_df,
                          balance_history_dec_df,
                          balance_history_sps_df,
                          balance_history_voucher_df,
                          single_season_id=None):
    season_end_times = season.get_season_end_times(time_zone)

    season_ratings = [0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 5100]
    # translate end rating to max (for graph)
    season_df['end_league_rating'] = season_df.apply(lambda row: season_ratings[row.league], axis=1)

    season_df['league_name'] = season_df.apply(lambda row: Leagues(row.league).name, axis=1)
    season_df['max_league_name'] = season_df.apply(lambda row: Leagues(row.max_league).name, axis=1)
    season_df['win_pct'] = season_df.apply(lambda row: (row.wins / row.battles * 100), axis=1)

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
                                                         'voucher_drop')

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
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_credits_df,
                                                         'season_rewards', column_prefix='credits_')

        # DEC add
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'dec_reward')
        season_df = cumulate_specific_balance_for_season(start_date, end_date, season_df, season_id,
                                                         balance_history_dec_df,
                                                         'quest_rewards', column_prefix='dec_')

        # NOTE SEASON REWARDS are always in the time frame of the next season
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

                    collect = collect.append(tournament_record, ignore_index=True)
    return collect


if __name__ == '__main__':
    main()
