import calendar
import datetime

import pytz
from dateutil import parser
from pytz import timezone

from src import api
from src.static_values_enum import Format


# determine last season start and end time
def get_previous_season_dates_and_id(time_zone):
    current_season_data = api.get_current_season()
    season_end_times = get_season_end_times(time_zone)
    previous_season_id = current_season_data['id'] - 1
    start_date = [season_end_time['date'] for season_end_time in season_end_times if
                  season_end_time["id"] == previous_season_id - 1][0]
    end_date = [season_end_time['date'] for season_end_time in season_end_times if
                season_end_time["id"] == previous_season_id][0]
    return start_date, end_date, previous_season_id


def print_new_season_dates():
    current_season_data = api.get_current_season()
    print("DETERMINE NEXT END SEASON (" + str(current_season_data['id']) + "), DATE: " + str(current_season_data['ends']))


def get_all_season_data(username, mode):
    print("Pulling season data (done per season so this can take a while)")
    season = api.get_current_season()
    current_season_id = season['id']
    season_array = []
    season_count = current_season_id
    if mode.value == Format.MODERN.value:
        # season 90 modern/wild is introduced
        season_count = current_season_id - 89
    for i in range(1, season_count):
        print("Pulling season data: " + str(current_season_id - i))
        player_result_season_x = api.get_leaderboard_with_player_season(username, current_season_id - i, mode)
        if 'season' in player_result_season_x:
            print("Get season data done (mode: " + str(mode.value) + "): " + str(current_season_id - i))
            season_array.append(player_result_season_x)
        else:
            # print("STOP no more (" + str(mode.value) + ") seasons found for  '" + str(username) + "'  last season: " + str(current_season_id - (i-1)))
            # break
            print("CONTINUE no data found for  (" + str(mode.value) + ") seasons found for  '" + str(username) + "'  season: " + str(current_season_id - i))
    return season_array


# Used information about season end dates from:
# https://kiokizz.github.io/Splinterlands/seasonReportCard/scripts/report_array.js?v=1
def get_season_end_times(time_zone):

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
        date = date.astimezone(timezone(time_zone))

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
            season['date'] = parser.parse("2021-08-16T20:00:00.000Z").astimezone(timezone(time_zone))
        # we have changed it to make seasons not end on weekends or holidays since there have been technical issues recently and we want the team to be available
        elif season['id'] == 86:
            season['date'] = parser.parse("2022-05-16T14:00:00.000Z").astimezone(timezone(time_zone))
        # Times provided by @yabapmatt
        elif season['id'] == 88:
            season['date'] = parser.parse("2022-06-15T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 89:
            season['date'] = parser.parse("2022-06-30T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 90:
            season['date'] = parser.parse("2022-07-13T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 91:
            season['date'] = parser.parse("2022-08-01T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 92:
            season['date'] = parser.parse("2022-08-16T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 93:
            season['date'] = parser.parse("2022-08-31T14:00:00.000Z").astimezone(timezone(time_zone))

        # Manual update
        elif season['id'] == 94:
            season['date'] = parser.parse("2022-09-15T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 96:
            season['date'] = parser.parse("2022-10-14T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 98:
            season['date'] = parser.parse("2022-11-15T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 100:
            season['date'] = parser.parse("2022-12-15T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 101:
            season['date'] = parser.parse("2022-12-29T15:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 102:
            season['date'] = parser.parse("2023-01-16T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 103:
            season['date'] = parser.parse("2023-01-31T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 104:
            season['date'] = parser.parse("2023-02-14T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 105:
            season['date'] = parser.parse("2023-02-28T14:00:00.000Z").astimezone(timezone(time_zone))
        elif season['id'] == 10:
            season['date'] = parser.parse("2023-03-15T14:00:00.000Z").astimezone(timezone(time_zone))

    return season_end_dates_array
