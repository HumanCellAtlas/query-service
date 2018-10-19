import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.isEnabledFor(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logging.root.addHandler(ch)
