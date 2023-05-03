import json
from datetime import datetime

import pytz
import requests
from dateutil import parser
from requests.adapters import HTTPAdapter
from src import season_variables
from src.logRetry import LogRetry

base_url_api2 = "https://api2.splinterlands.com/"
hive_api_url = 'https://api.hive.blog'

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)


def get_current_season():
    # This only have to be done once.
    if not season_variables.current_season:
        address = base_url_api2 + "settings"
        season_variables.current_season = http.get(address).json()['season']

    return season_variables.current_season


def get_season_end_times():
    # This only have to be done once.
    if not season_variables.season_end_dates_array:
        season = get_current_season()
        till_season_id = season['id']
        print("Retrieve season end dates for '" + str(till_season_id) + "' seasons")
        # https://api.splinterlands.com/season?id=1
        season_variables.season_end_dates_array = []

        for season in range(1, till_season_id + 1):
            address = base_url_api2 + "season?id=" + str(season)
            result = http.get(address)
            if result.status_code == 200:
                date = parser.parse(str(result.json()['ends']))
                season_variables.season_end_dates_array.append({'id': season, 'date': date})
            else:
                print("Failed call: '" + str(address) + "'")
                print("Unable to determine season end date return code: " + str(result.status_code))
                print("This interrupts all other calculations, try re-execution.")
                print("Stopping program now ... ")
                exit(1)

    return season_variables.season_end_dates_array


def get_leaderboard_with_player_season(username, season, mode):
    address = base_url_api2 + \
              "players/leaderboard_with_player?season=" + str(season) + \
              "&format=" + str(mode.value) + \
              "&username=" + str(username)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()['player']
    else:
        return None


def get_player_history_rewards(username):
    address = base_url_api2 + "players/history?username=" + str(
        username) + "&from_block=-1&limit=500&types=card_award,claim_reward"
    return http.get(address).json()


def get_balance_history_for_token(username, token="DEC", from_date=None, unclaimed_sps=False):
    limit = 1000
    offset = 0
    max_transactions = 1000000
    print_suffix = ""

    if unclaimed_sps:
        print_suffix = " UNCLAIMED"

    complete_result = current_result = get_balance_history_for_token_impl(username,
                                                                          token=token,
                                                                          offset=offset,
                                                                          limit=limit,
                                                                          unclaimed_sps=unclaimed_sps)

    while len(current_result) > 0 and offset <= max_transactions:
        print(str(token) + str(print_suffix) +
              ": More then '" + str(offset + limit) +
              "' returned, continue for another balance pull...")
        current_result = get_balance_history_for_token_impl(username,
                                                            token=token,
                                                            offset=offset + limit,
                                                            limit=limit,
                                                            unclaimed_sps=unclaimed_sps)
        complete_result += current_result
        offset += limit
        created_date = parser.parse(complete_result[-1]['created_date'])
        if from_date and from_date > created_date:
            print(token + ": last pull contains all season information data from '" + str(from_date) + "' till NOW")
            break

    if offset > max_transactions:
        print("Stop pulling data MAX transactions (" + str(max_transactions) + ") reached. Possible not all data pulled")
    print(token + ": all data pulled")

    return complete_result


def get_balance_history_for_token_impl(username, token="DEC", offset=0, limit=1000, unclaimed_sps=False):
    token_types = ["SPS", "DEC", "VOUCHER", "CREDITS", "MERITS"]
    if token not in token_types:
        raise ValueError("Invalid token type. Expected one of: %s" % token_types)

    if unclaimed_sps:
        balance_history_link = "players/unclaimed_balance_history?token_type="
    else:
        balance_history_link = "players/balance_history?token_type="
    address = base_url_api2 + str(balance_history_link) + str(token) + "&username=" + str(
        username) + "&offset=" + str(offset) + "&limit=" + str(limit)

    response = http.get(address)
    if response.status_code == 200 and response.text != '':
        return response.json()
    else:
        return []


def get_card_details():
    address = base_url_api2 + "cards/get_details"
    return http.get(address).json()


def get_tournament(tournament_id):
    address = base_url_api2 + "tournaments/find?id=" + str(tournament_id)
    return http.get(address).json()


def get_player_tournaments_ids(username):
    address = base_url_api2 + "players/history?username=" + str(
        username) + "&from_block=-1&limit=500&types=token_transfer"
    result = http.get(address).json()
    tournaments_transfers = list(filter(lambda item: "enter_tournament" in item['data'], result))
    tournaments_ids = []
    for tournament in tournaments_transfers:
        tournaments_ids.append(json.loads(tournament['data'])['tournament_id'])
    return tournaments_ids


def get_cards_by_ids(ids):
    #https://api.splinterlands.io/cards/find?ids=C3-457-3VIL75QJ2O,
    address = base_url_api2 + "cards/find?ids=" + str(ids)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_spl_transaction(trx_id):
    # https://api.splinterlands.io/market/status?id=d8f8593d637ebdd0bca7994dd7e1a15d9f12efa7-0
    address = base_url_api2 + "market/status?id=" + str(trx_id)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_hive_transactions(account_name, from_date, till_date, last_id, results):
    limit = 1000
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = '{"jsonrpc":"2.0", ' \
           '"method":"condenser_api.get_account_history", ' \
           '"params":["' + str(account_name) + '" , ' \
           + str(last_id) + ', ' \
           + str(limit) + ', 262144], "id":1}'

    response = http.post(hive_api_url, headers=headers, data=data)
    if response.status_code == 200:
        transactions = json.loads(response.text)['result']
        for transaction in transactions:
            timestamp = transaction[1]['timestamp']
            # Assume time of Hive is always UTC
            # https://developers.hive.io/tutorials-recipes/understanding-dynamic-global-properties.html#time
            timestamp = datetime.strptime(timestamp + "-+0000", '%Y-%m-%dT%H:%M:%S-%z')
            if from_date < timestamp < till_date:
                results.append(transaction[1])

        # Check last transaction if there need to be another pull
        timestamp = transactions[0][1]['timestamp']
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').astimezone(pytz.utc)
        if from_date < timestamp:
            last_id = transactions[0][0]

            get_hive_transactions(account_name, from_date, till_date, last_id-1, results)
    return results


def get_settings():
    address = base_url_api2 + "settings"
    return requests.get(address).json()
