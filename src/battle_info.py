import os

import pandas as pd

from src import configuration, api, season
from src.static_values_enum import Leagues


def get_battle_info(account_name, battle_info_file, mode):
    current_season_data = api.get_current_season()

    if os.path.isfile(battle_info_file):
        season_battle_df = pd.read_csv(battle_info_file, index_col=[0])
        next_season = season_battle_df.season.max() + 1

        if season_battle_df.season.max() != current_season_data['id'] - 1:
            for season_id in range(next_season, current_season_data['id']):
                print("Get battle information (" + str(mode.value) + ") of season: " + str(season_id))
                season_info = api.get_leaderboard_with_player_season(account_name, season_id, mode=mode)
                if season_info and len(season_info) > 1:
                    season_battle_df_new = pd.DataFrame(season_info, index=[0])
                    season_battle_df_new = add_battle_data_to_seasons_df(season_battle_df_new)
                else:
                    season_battle_df_new = pd.DataFrame({'season': season_id, 'player': account_name}, index=[0])
                season_battle_df = pd.concat([season_battle_df, season_battle_df_new], ignore_index=True)
        else:
            print("All battle information for mode " + str(mode.value) + " already pulled continue with the current data set")

    else:
        season_battle_df = pd.DataFrame(season.get_all_season_data(account_name, mode))
        season_battle_df = add_battle_data_to_seasons_df(season_battle_df)

    season_battle_df.to_csv(battle_info_file)
    return season_battle_df


def add_battle_data_to_seasons_df(season_df):
    season_ratings = [0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 5100]

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
