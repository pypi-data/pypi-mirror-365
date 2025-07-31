# this_file: src/tscprojpy/serialization/saver.py
"""Project saver for serializing Camtasia projects."""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from ..models import Project
from .json_encoder import CamtasiaJSONEncoder


class ProjectSaver:
    """Saves and serializes Camtasia project files."""

    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        """Initialize saver.

        Args:
            indent: JSON indentation level
            ensure_ascii: If True, escape non-ASCII characters
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    def save_file(self, project: Project, file_path: str | Path) -> None:
        """Save project to file.

        Args:
            project: Project to save
            file_path: Path to save to
        """
        path = Path(file_path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving project to: {path}")

        # Convert to dictionary
        data = self.project_to_dict(project)

        # Write JSON with custom encoder
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data, f, indent=self.indent, ensure_ascii=self.ensure_ascii, 
                separators=(",", ": "), cls=CamtasiaJSONEncoder
            )

        logger.info("Project saved successfully")

    def save_dict(self, data: dict[str, Any], file_path: str | Path) -> None:
        """Save dictionary data to file.

        Args:
            data: Dictionary data to save
            file_path: Path to save to
        """
        path = Path(file_path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving data to: {path}")

        # Write JSON with custom encoder
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data, f, indent=self.indent, ensure_ascii=self.ensure_ascii, 
                separators=(",", ": "), cls=CamtasiaJSONEncoder
            )

    def project_to_dict(self, project: Project) -> dict[str, Any]:
        """Convert project to dictionary for serialization.

        Args:
            project: Project to convert

        Returns:
            Dictionary representation
        """
        return project.to_dict()

    def to_json_string(self, project: Project) -> str:
        """Convert project to JSON string.

        Args:
            project: Project to convert

        Returns:
            JSON string representation
        """
        data = self.project_to_dict(project)
        return json.dumps(
            data, indent=self.indent, ensure_ascii=self.ensure_ascii, 
            separators=(",", ": "), cls=CamtasiaJSONEncoder
        )
