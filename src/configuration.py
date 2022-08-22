import configparser

config = configparser.RawConfigParser()
config.read('config.properties')

time_zone = config.get('settings', 'time_zone')
ACCOUNT_NAME = config.get('settings', 'account_name')
