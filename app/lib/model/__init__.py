from .bundle import *
from .file import *
from .metadata import *

from datetime import datetime


def datetime_to_version(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%dT%H%M%S.%fZ")
