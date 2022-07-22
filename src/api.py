import json

import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter

base_url_api2 = "https://api2.splinterlands.com/"
base_url_api = "https://api.splinterlands.com/"
cached_url = "https://cache-api.splinterlands.com/"
LIMIT = 500


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

    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
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


def get_balance_history_for_token(username, token="DEC", offset=0, result=None):
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

    if result is None:  # create a new result if no intermediate was given
        result = requests.get(address).json()
    else:
        result += requests.get(address).json()

    if len(result) == offset + LIMIT:
        print(token + ": More then '" + str(offset + LIMIT) + "' returned, continue for another balance pull...")
        get_balance_history_for_token(username, token=token, offset=offset + LIMIT, result=result)
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


def get_battle_history(username, number_of_battles, mode):
    address = base_url_api2 + "battle/history2?player=" + username + \
             "&leaderboard=0&limit=" + str(number_of_battles) + \
             "&format=" + str(mode.value)
    result = requests.get(address).json()
    return result['battles']
