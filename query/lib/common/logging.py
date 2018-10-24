import logging
import os
import sys


def get_logger(name):
    ch = logging.StreamHandler(sys.stdout)
    log_level_name = os.environ['LOG_LEVEL'] if 'LOG_LEVEL' in os.environ else 'DEBUG'
    log_level = getattr(logging, log_level_name.upper())
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s',
                                  datefmt="%Y-%m-%dT%H:%M:%S%z")
    ch.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    return logger


def format_logger_with_id(logger, corr_id_name, corr_id_val):
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s' +
                                  f' corr_id:{corr_id_name}:{corr_id_val} %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z")
    logger.handlers[0].setFormatter(formatter)
    return logger
