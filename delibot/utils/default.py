import configparser
import logging

log = logging.getLogger()


def get_config():
    config = configparser.ConfigParser()

    try:
        config.read_file(open('config/config.ini', 'r'))
    except FileNotFoundError as e:
        log.critical(f'Could not find the configuration file. Reason: {e}')
        exit()

    return config
