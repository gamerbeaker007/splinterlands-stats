import configparser

config = configparser.RawConfigParser()
config.read('config.properties')

ACCOUNT_NAMES = config.get('settings', 'account_names')
SKIP_ZEROS = config.get('settings', 'skip_zeros')
