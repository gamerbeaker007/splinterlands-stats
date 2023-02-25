import json

import numpy as np
import pandas as pd

from src import configuration, api
from src.api import get_hive_transactions, get_spl_transaction, get_cards_by_ids
from src.static_values_enum import Edition


def get_last_season_market_history(account_name, start_date, end_date):
    market_history_df = pd.DataFrame(api.get_market_history(account_name))
    if not market_history_df.empty:
        last_season_market_history = filter_df_last_season(start_date, end_date, market_history_df)
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


def get_last_season_player_history_rewards(account_name, start_date, end_date, season_id):
    player_history_df = pd.DataFrame(api.get_player_history_rewards(account_name))
    reward_data = pd.DataFrame()

    if not player_history_df.empty:
        # Find season reward
        for index, row in player_history_df.iterrows():
            data = json.loads(row.data)
            if row.success and data['type'] == 'league_season' and data['season'] == season_id:
                reward_data = pd.concat([reward_data, pd.DataFrame(json.loads(row.result)['rewards'])], ignore_index=True)
                break

        last_season_player_history_rewards = filter_df_last_season(start_date, end_date, player_history_df)

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


def find_card_name(card_details_list, card_id):
    return list(filter(lambda card_details_dict: card_details_dict['id'] == card_id, card_details_list))[0]['name']


def filter_df_last_season(start_date, end_date, data_frame):
    if not data_frame.empty:
        # make sure created_date is of type time date
        date_field = 'created_date'
        data_frame[date_field] = pd.to_datetime(data_frame[date_field])

        # create mask, filter all date between season start and season end date
        mask = (data_frame[date_field] > start_date) & (data_frame[date_field] <= end_date)
        return data_frame.loc[mask].copy()
    return data_frame


# def determine_card_level(combine_rates, core_editions, edition, xp):
#     for core_edition in core_editions:
#         if core_edition == edition:
#             selected_edition = core_edition
#             break
#         if core_edition > edition:
#             print("edition to far so -1 " + str(core_edition))
#             break
#
#     print(selected_edition)
#     return


def get_sold_cards(account_name, cards_df):
    sold_cards = []
    if not cards_df.empty:
        # first remove duplicate card ids
        cards_df = cards_df.drop_duplicates()

        ids = ','.join(cards_df['card'].values.tolist())
        cards = get_cards_by_ids(ids)
        for card in cards:
            if card['player'] != account_name:
                sold_cards += [card]
    return sold_cards


def get_purchased_sold_cards(account_name, start_date, end_date):
    card_details_list = api.get_card_details()

    transactions = []
    transactions = get_hive_transactions(account_name, start_date, end_date, -1, transactions)

    # filter purchase transactions
    sm_market_purchase = pd.DataFrame()
    potential_sell = pd.DataFrame()
    for transaction in transactions:
        operation = transaction['op'][1]
        if operation['id'] == 'sm_market_purchase':
            df1 = pd.DataFrame({'spl_id': json.loads(operation['json'])['items']})
            sm_market_purchase = pd.concat([sm_market_purchase, df1])
        elif operation['id'] == 'sm_sell_cards':
            cards = json.loads(operation['json'])
            for card in cards:
                df1 = pd.DataFrame({'card': card['cards']})
                potential_sell = pd.concat([potential_sell, df1])

    # process purchases
    purchases = pd.DataFrame()
    if not sm_market_purchase.empty:
        sm_market_purchase = sm_market_purchase.reset_index(drop=True)
        count = sm_market_purchase.count().values[0]
        print("Number card to get: " + str())
        for index, row in sm_market_purchase.iterrows():
            print("Get card transaction: " + str(index) + "/" + str(count))
            # TODO look into a way to parallel process
            result = get_spl_transaction(row.values[0])
            purchases = pd.concat([purchases, pd.DataFrame(result['cards'])])

        purchases['edition_name'] = purchases.apply(
            lambda row: (Edition(row.edition)).name, axis=1)
        purchases['card_name'] = purchases.apply(
            lambda row: find_card_name(card_details_list, row.card_detail_id), axis=1)

    sold_cards = pd.DataFrame(get_sold_cards(account_name, potential_sell))
    if not sold_cards.empty:
        sold_cards['edition_name'] = sold_cards.apply(
            lambda row: (Edition(row.edition)).name, axis=1)
        sold_cards['card_name'] = sold_cards.apply(
            lambda row: find_card_name(card_details_list, row.card_detail_id), axis=1)

    return purchases, sold_cards

