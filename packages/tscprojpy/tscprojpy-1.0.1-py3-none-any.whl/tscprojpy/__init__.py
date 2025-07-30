# this_file: tscprojpy/src/tscprojpy/__init__.py
"""tscprojpy - A modern Python project template."""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
