import json
from datetime import datetime

import pytz
import requests
from dateutil import parser
from urllib3 import Retry
from requests.adapters import HTTPAdapter

base_url_api2 = "https://api2.splinterlands.com/"
base_url_api = "https://api.splinterlands.com/"
cached_url = "https://cache-api.splinterlands.com/"
hive_api_url = 'https://api.hive.blog'
LIMIT = 500

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)


def get_current_season():
    address = base_url_api2 + "settings"
    return requests.get(address).json()['season']


def get_combine_rates():
    address = base_url_api2 + "settings"
    return requests.get(address).json()['combine_rates'], requests.get(address).json()['combine_rates_gold'], \
           requests.get(address).json()['core_editions']


def get_specific_season_end_date(season):
    address = base_url_api2 + ""
    return requests.get(address).json()


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


def get_market_history(username):
    address = base_url_api2 + "market/history?player=" + str(username)
    return requests.get(address).json()


def get_player_history_rewards(username):
    address = base_url_api + "players/history?username=" + str(
        username) + "&from_block=-1&limit=500&types=card_award,claim_reward"
    return requests.get(address).json()


def get_balance_history_for_token(username, token="DEC", offset=0, result=None, from_date=None):
    token_types = ["SPS", "DEC", "VOUCHER", "CREDITS", "MERITS"]
    if token not in token_types:
        raise ValueError("Invalid token type. Expected one of: %s" % token_types)

    address = base_url_api2 + "players/balance_history?token_type=" + str(token) + "&username=" + str(
        username) + "&offset=" + str(offset) + "&limit=" + str(LIMIT)
    # if token == "DEC":
    # all found :
    # dec_reward
    # rental_payment_fee
    # rental_payment
    # season_rewards
    # tournament_prize
    # quest_rewards
    # withdraw
    # token_transfer
    # market_purchase
    # enter_tournament
    # market_rental
    # rental_refund
    # address = str(address) + "&types=rental_payment_fees,market_rental,rental_payment,rental_refund,leaderboard_prizes,dec_reward,season_rewards"

    response = http.get(address)
    if response.status_code == 200:
        if result is None:  # create a new result if no intermediate was given
            result = response.json()
        else:
            result += response.json()

    if len(result) == offset + LIMIT:
        created_date = parser.parse(result[-1]['created_date'])
        if not from_date or from_date < created_date:
            print(token + ": More then '" + str(offset + LIMIT) + "' returned, continue for another balance pull...")
            get_balance_history_for_token(username, token=token, offset=offset + LIMIT, result=result, from_date=from_date)
        else:
            print(token + ": last pull contains all season information data from '" + str(from_date) + "' till NOW")
    else:
        print(token + ": all data pulled")

    return result


def get_balance_history_for_token_unclaimed(username, token="SPS", offset=0, result=None, from_date=None):
    token_types = ["SPS"]
    if token not in token_types:
        raise ValueError("Invalid token type. Expected one of: %s" % token_types)

    address = base_url_api2 + "players/unclaimed_balance_history?token_type=" + str(token) + "&username=" + str(
        username) + "&offset=" + str(offset) + "&limit=" + str(LIMIT)

    if result is None:  # create a new result if no intermediate was given
        result = requests.get(address).json()
    else:
        result += requests.get(address).json()

    if len(result) == offset + LIMIT:
        created_date = parser.parse(result[-1]['created_date'])
        if not from_date or from_date < created_date:
            print(token + " UNCLAIMED: More then '" + str(offset + LIMIT) + "' returned, continue for another balance pull...")
            get_balance_history_for_token_unclaimed(username, token=token, offset=offset + LIMIT, result=result, from_date=from_date)
        else:
            print(token + " UNCLAIMED: last pull contains all season information data from '" + str(from_date) + "' till NOW")
    else:
        print(token + "UNCLAIMED: all data pulled")

    return result


def get_market_transaction(trx_id):
    address = base_url_api2 + "market/status?id=" + str(trx_id)
    return requests.get(address).json()


def get_card_details():
    address = base_url_api2 + "cards/get_details"
    return requests.get(address).json()


def get_tournament(tournament_id):
    address = base_url_api2 + "tournaments/find?id=" + str(tournament_id)
    return requests.get(address).json()


def get_player_tournaments_ids(username):
    address = base_url_api2 + "players/history?username=" + str(
        username) + "&from_block=-1&limit=500&types=token_transfer"
    result = requests.get(address).json()
    tournaments_transfers = list(filter(lambda item: "enter_tournament" in item['data'], result))
    tournaments_ids = []
    for tournament in tournaments_transfers:
        tournaments_ids.append(json.loads(tournament['data'])['tournament_id'])
    return tournaments_ids


def get_cards_by_ids(ids):
    #https://api.splinterlands.io/cards/find?ids=C3-457-3VIL75QJ2O,
    address = base_url_api + "cards/find?ids=" + str(ids)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_spl_transaction(trx_id):
    # https://api.splinterlands.io/market/status?id=d8f8593d637ebdd0bca7994dd7e1a15d9f12efa7-0
    address = base_url_api + "market/status?id=" + str(trx_id)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_hive_transactions(account_name, from_date, till_date, last_id, results):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = '{"jsonrpc":"2.0", ' \
           '"method":"condenser_api.get_account_history", ' \
           '"params":["' + str(account_name) + '" , ' \
           + str(last_id) + ', ' \
           + str(LIMIT) + ', 262144], "id":1}'

    response = requests.post(hive_api_url, headers=headers, data=data)
    if response.status_code == 200:
        transactions = json.loads(response.text)['result']
        for transaction in transactions:
            timestamp = transaction[1]['timestamp']
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').astimezone(pytz.utc)
            if from_date < timestamp < till_date:
                results.append(transaction[1])

        # Check last transaction if there need to be another pull
        timestamp = transactions[0][1]['timestamp']
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').astimezone(pytz.utc)
        if from_date < timestamp:
            last_id = transactions[0][0]

            get_hive_transactions(account_name, from_date, till_date, last_id-1, results)
    return results
