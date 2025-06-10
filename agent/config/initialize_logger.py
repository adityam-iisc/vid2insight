import logging.config
import os

from ruamel.yaml import YAML


def read_logger_config():
    yaml = YAML(typ='safe')
    logger_config_path = os.path.join(os.path.dirname(__file__), 'logger_config.yaml')

    try:
        with open(logger_config_path, 'r') as f:
            return yaml.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Logger configuration file not found at {logger_config_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while loading the logger configuration: {e}")


# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'team-11': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}


def setup_logger():
    # logger_config = read_logger_config()
    # logging.config.dictConfig(logger_config)
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('team-11')


logger = setup_logger()
