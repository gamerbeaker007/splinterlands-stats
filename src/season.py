import calendar
import datetime

import pytz
from pytz import timezone

from src import api


def get_all_season_data(username):
    print("Pulling season data (done per season so this can take a while)")
    season = api.get_current_season()
    current_season_id = season['id']
    season_array = []
    for i in range(1, current_season_id):
        print("Pulling season data: " + str(current_season_id - i))
        player_result_season_x = api.get_leaderboard_with_player_season(username, current_season_id - i)
        if 'season' in player_result_season_x:
            print("Get season data done: " + str(current_season_id - i))
            season_array.append(player_result_season_x)
        else:
            print("STOP no more seasons found for  '" + str(username) + "'  last season: " + str(current_season_id - (i-1)))
            break
    return season_array


def get_season_end_times(time_zone_str):
    # season origin
    x = {
        "id": 55,
        "YYYY": 2021,
        "MM": 1,
        "DD": 31,
        "HH": 14
    }

    hours = [2, 8, 14, 20]
    season_end_dates_array = []
    for i in range(0, 240):
        date = datetime.datetime(x['YYYY'], month=x['MM'], day=x['DD'], hour=x['HH'], tzinfo=pytz.utc)
        date = date.astimezone(timezone(time_zone_str))

        season_dict = {
            "id": x['id'] + i,
            "date": date #date.strftime('%Y-%m-%dT%H:%M:%S') + str(".000Z")
        }
        season_end_dates_array.append(season_dict)

        if x['DD'] == 15:
            # last day of this month
            x['DD'] = calendar.monthrange(x['YYYY'], x['MM'])[1]
        else:
            # next month
            x['DD'] = 15
            if x['MM'] == 12:
                x['YYYY'] = x['YYYY'] + 1
                x['MM'] = 1
            else:
                x['MM'] = x['MM'] + 1
        # HH
        cycle = hours.index(x['HH'])
        # select the next xHH
        if cycle == 3:
            x['HH'] = hours[0]
        else:
            x['HH'] = hours[cycle + 1]

    # Manual overrides for adjustments
    # Season 55, id:68 due to server migration issues:
    # https://discord.com/channels/447924793048825866/451123773882499085/876471197708206090
    for season in season_end_dates_array:
        if season['id'] == 68:
            season['date'] = "2021-08-16T20:00:00.000Z"
    return season_end_dates_array
