import logging
import sys

from bot.config import LOG_FORMAT, LOG_ALL_FILE


def get_logger(name):
    COMMON_LEVEL = logging.DEBUG
    formatter = logging.Formatter(LOG_FORMAT)

    log = logging.getLogger(name)
    log.setLevel(COMMON_LEVEL)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(COMMON_LEVEL)
    stdout.setFormatter(formatter)

    all = logging.FileHandler(LOG_ALL_FILE)
    all.setLevel(COMMON_LEVEL)
    all.setFormatter(formatter)

    log.addHandler(stdout)
    log.addHandler(all)
    return log
