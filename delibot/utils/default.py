import configparser
import logging
from pathlib import Path
log = logging.getLogger()


def get_config():
    config = configparser.ConfigParser()

    file_path = Path('config/config.ini')

    if file_path.exists():
        config.read_file(open(file_path, 'r'))
    else:
        log.critical(f'Could not find the configuration file located at "{file_path.absolute()}".')
        exit()

    return config
