# this_file: src/tscprojpy/models/__init__.py
"""Domain models for Camtasia project structure."""

from .canvas import Canvas
from .media import AMFile, AudioMedia, Callout, IMFile, ImageMedia, Media, VideoMedia, VMFile
from .project import Project, ProjectMetadata
from .source import SourceBin, SourceItem, SourceTrack
from .timeline import Timeline, Track, Transition

__all__ = [
    # Core project structure
    "Project",
    "ProjectMetadata",
    "Canvas",
    # Source media
    "SourceBin",
    "SourceItem",
    "SourceTrack",
    # Timeline structure
    "Timeline",
    "Track",
    "Transition",
    # Media types
    "Media",
    "VideoMedia",
    "AudioMedia",
    "ImageMedia",
    "Callout",
    # Specific media file types
    "VMFile",
    "AMFile",
    "IMFile",
]