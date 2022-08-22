import json
from datetime import datetime

import pandas as pd
import pytz

from src import api
from src.static_values_enum import RatingLevel


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

                    prize_qty = "0"
                    prize_type = ""
                    if player_data['prize']:
                        prize_qty = player_data['prize']
                    else:
                        if player_data['ext_prize_info']:
                            prize_info = json.loads(player_data['ext_prize_info'])
                            prize_qty = prize_info[0]['qty']
                            prize_type = prize_info[0]['type']

                    tournament_record = {
                        'name': tournament['name'],
                        'league': RatingLevel(tournament['data']['rating_level']).name,
                        'num_players': tournament['num_players'],
                        'finish': player_data['finish'],
                        'wins': player_data['wins'],
                        'losses': player_data['losses'],
                        'draws': player_data['draws'],
                        'entry_fee': player_data['fee_amount'],
                        'prize_qty': prize_qty,
                        'prize_type': prize_type
                    }
                    collect = pd.concat([collect, pd.DataFrame(tournament_record, index=[0])], ignore_index=True)
    return collect
