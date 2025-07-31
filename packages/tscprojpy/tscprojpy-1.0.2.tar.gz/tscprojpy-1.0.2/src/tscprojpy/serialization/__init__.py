# this_file: src/tscprojpy/serialization/__init__.py
"""Serialization and deserialization for Camtasia projects."""

from .loader import ProjectLoader
from .saver import ProjectSaver
from .version import ProjectVersion, detect_version, get_version_features, is_supported_version
from .json_encoder import CamtasiaJSONEncoder

__all__ = [
    "ProjectLoader",
    "ProjectSaver",
    "ProjectVersion",
    "detect_version",
    "get_version_features",
    "is_supported_version",
    "CamtasiaJSONEncoder",
]
