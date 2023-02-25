import configparser

config = configparser.RawConfigParser()
config.read('config.properties')

TIME_ZONE = config.get('settings', 'time_zone')
ACCOUNT_NAMES = config.get('settings', 'account_names')
SKIP_ZEROS = config.get('settings', 'skip_zeros')
