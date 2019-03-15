from .bundle import BundleManifest, Bundle
from .file import File
from .metadata import FileMetadata

from datetime import datetime


def datetime_to_version(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%dT%H%M%S.%fZ")
