# this_file: src/tscprojpy/__init__.py
"""tscprojpy - Tools for manipulating Camtasia .tscproj files."""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

# Import main components
from .models import (
    Canvas,
    Project,
    ProjectMetadata,
    SourceBin,
    SourceItem,
    Timeline,
    Track,
)
from .serialization import ProjectLoader, ProjectSaver
from .transforms import PropertyTransformer, TransformConfig, TransformType

__all__ = [
    "Canvas",
    # Core models
    "Project",
    # Serialization
    "ProjectLoader",
    "ProjectMetadata",
    "ProjectSaver",
    # Transforms
    "PropertyTransformer",
    "SourceBin",
    "SourceItem",
    "Timeline",
    "Track",
    "TransformConfig",
    "TransformType",
    "__version__",
]
