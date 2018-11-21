from query.lib.model.bundle import *
from query.lib.model.file import *
from query.lib.model.metadata import *

from datetime import datetime


def datetime_to_version(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%dT%H%M%S.%fZ")
