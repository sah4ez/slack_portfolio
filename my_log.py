import sys
import config
import logging


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(level=logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(config.LOG_FORMAT)
    ch.setFormatter(formatter)

    log.addHandler(ch)
    return log
