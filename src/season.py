from src import api
from src.static_values_enum import Format


# determine last season start and end time
def get_previous_season_dates_and_id():
    current_season_data = api.get_current_season()
    season_end_times = api.get_season_end_times()
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
