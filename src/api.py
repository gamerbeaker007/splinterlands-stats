import requests

base_url = "https://api2.splinterlands.com/"
cached_url = "https://cache-api.splinterlands.com/"
LIMIT = 500


def get_current_season():
    address = base_url + "settings"
    return requests.get(address).json()['season']


def get_combine_rates():
    address = base_url + "settings"
    return requests.get(address).json()['combine_rates'], requests.get(address).json()['combine_rates_gold'], requests.get(address).json()['core_editions']


def get_specific_season_end_date(season):
    address = base_url + ""
    return requests.get(address).json()


def get_leaderboard_with_player_season(username, season):
    address = base_url + "players/leaderboard_with_player?season=" + str(season) + "&username=" + str(username)
    return requests.get(address).json()['player']


def get_market_history(username):
    address = base_url + "market/history?player=" + str(username)
    return requests.get(address).json()


def get_balance_history_for_token(username, token="DEC", offset=0, result=None):
    token_types = ["SPS", "DEC", "VOUCHER", "CREDITS"]
    if token not in token_types:
        raise ValueError("Invalid token type. Expected one of: %s" % token_types)

    address = base_url + "players/balance_history?token_type=" + str(token) + "&username=" + str(username) + "&offset=" + str(offset) + "&limit=" + str(LIMIT)
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

    if len(result) == offset+LIMIT:
        print("More then '" + str(offset+LIMIT) + "' returned, continue for another balance pull...")
        get_balance_history_for_token(username, token=token, offset=offset+LIMIT, result=result)
    return result


def get_market_transaction(trx_id):
    address = base_url + "market/status?id=" + str(trx_id)
    return requests.get(address).json()


def get_card_details():
    address = base_url + "cards/get_details"
    return requests.get(address).json()
