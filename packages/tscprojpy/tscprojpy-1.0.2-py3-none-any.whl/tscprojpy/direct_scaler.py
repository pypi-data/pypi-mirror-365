# this_file: src/tscprojpy/direct_scaler.py
"""Direct JSON-based scaler that preserves all properties."""

import json
import math
from pathlib import Path
from typing import Any

from loguru import logger
from .serialization import CamtasiaJSONEncoder


class DirectScaler:
    """Scale Camtasia projects directly on JSON data, preserving all properties."""

    def __init__(self, scale_factor: float, verbose: bool = False):
        """Initialize scaler with scale factor.
        
        Args:
            scale_factor: Factor to scale by (e.g., 1.5 for 150%)
            verbose: Enable verbose logging
        """
        self.scale_factor = scale_factor
        self.verbose = verbose
        
        # Define spatial properties to scale
        self.scale_properties = {
            # Canvas and object dimensions
            "width", "height",
            "widthAttr", "heightAttr",
            
            # Translation/position properties
            "translation0", "translation1", "translation2",
            
            # Scale properties (these multiply with existing scale)
            "scale0", "scale1", "scale2",
            
            # Crop properties
            "geometryCrop0", "geometryCrop1", "geometryCrop2", "geometryCrop3",
            
            # Shape properties
            "corner-radius", "stroke-width",
            
            # Default values for various objects
            "default-width", "default-height",
            "default-translation0", "default-translation1", "default-translation2",
            "default-scale",  # Single scale value
            "default-scale0", "default-scale1", "default-scale2",  # Component scale values
        }
        
        # Properties that should NOT be scaled
        self.preserve_properties = {
            "sampleRate",  # Keep as string fractions
            "integratedLUFS",  # Can have extreme values
            "peakLevel",
        }

    def scale_file(self, input_path: str | Path, output_path: str | Path) -> None:
        """Scale a project file and save the result.
        
        Args:
            input_path: Path to input .tscproj file
            output_path: Path to save scaled file
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if self.verbose:
            logger.info(f"Loading project from: {input_path}")
        
        # Load JSON preserving all formatting
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Fix any special values that were loaded as infinity
        data = self._fix_special_values(data)
        
        # Scale the data
        scaled_data = self.scale_data(data)
        
        if self.verbose:
            logger.info(f"Saving scaled project to: {output_path}")
        
        # Save with proper formatting and custom encoder
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(scaled_data, f, indent=2, ensure_ascii=False, 
                     separators=(",", ": "), cls=CamtasiaJSONEncoder)
    
    def _fix_special_values(self, obj: Any) -> Any:
        """Fix special float values before scaling.
        
        Args:
            obj: Object to fix
            
        Returns:
            Fixed object
        """
        if isinstance(obj, float):
            if math.isinf(obj):
                if obj < 0:
                    return -1.7976931348623157e+308  # Safe minimum
                else:
                    return 1.7976931348623157e+308   # Safe maximum  
            elif math.isnan(obj):
                return 0.0
            return obj
        elif isinstance(obj, dict):
            return {k: self._fix_special_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._fix_special_values(item) for item in obj]
        return obj
    
    def scale_data(self, data: dict) -> dict:
        """Scale project data while preserving all properties.
        
        Args:
            data: Project dictionary
            
        Returns:
            Scaled project dictionary
        """
        # Scale canvas dimensions at root level
        if "width" in data:
            if self.verbose:
                logger.info(f"Scaling width: {data['width']} * {self.scale_factor}")
            scaled_width = data["width"] * self.scale_factor
            # Preserve integer type if original was integer
            if isinstance(data["width"], int):
                data["width"] = int(round(scaled_width))
            else:
                data["width"] = scaled_width
            if self.verbose:
                logger.info(f"Result: {data['width']}")
        if "height" in data:
            if self.verbose:
                logger.info(f"Scaling height: {data['height']} * {self.scale_factor}")
            scaled_height = data["height"] * self.scale_factor
            # Preserve integer type if original was integer
            if isinstance(data["height"], int):
                data["height"] = int(round(scaled_height))
            else:
                data["height"] = scaled_height
            if self.verbose:
                logger.info(f"Result: {data['height']}")
        
        # Recursively scale all nested properties (excluding root level which we already handled)
        for key, value in data.items():
            if key not in ("width", "height") and isinstance(value, (dict, list)):
                self._scale_recursive(value, key)
        
        return data
    
    def _scale_recursive(self, obj: Any, parent_key: str | None = None) -> None:
        """Recursively scale values in place.
        
        Args:
            obj: Object to scale (dict, list, or value)
            parent_key: Parent key for context
        """
        if isinstance(obj, dict):
            for key, value in list(obj.items()):  # list() to allow modification
                # Handle special cases
                if key == "rect" and isinstance(value, list) and len(value) == 4:
                    # Scale rect arrays [x, y, width, height] - preserve integer types
                    scaled_values = []
                    for v in value:
                        scaled = v * self.scale_factor
                        # Preserve integer type if original was integer
                        if isinstance(v, int):
                            scaled_values.append(int(round(scaled)))
                        else:
                            scaled_values.append(scaled)
                    obj[key] = scaled_values
                elif key == "trackRect" and isinstance(value, list) and len(value) == 4:
                    # Scale trackRect arrays - preserve integer types
                    scaled_values = []
                    for v in value:
                        scaled = v * self.scale_factor
                        # Preserve integer type if original was integer
                        if isinstance(v, int):
                            scaled_values.append(int(round(scaled)))
                        else:
                            scaled_values.append(scaled)
                    obj[key] = scaled_values
                elif key == "keyframes" and isinstance(value, list):
                    # Handle keyframes
                    for kf in value:
                        if isinstance(kf, dict) and "value" in kf and parent_key in self.scale_properties:
                            if isinstance(kf["value"], (int, float)):
                                scaled = kf["value"] * self.scale_factor
                                # Preserve integer type if original was integer
                                if isinstance(kf["value"], int):
                                    kf["value"] = int(round(scaled))
                                else:
                                    kf["value"] = scaled
                elif key in self.scale_properties and key not in self.preserve_properties:
                    # Scale regular properties
                    if isinstance(value, (int, float)):
                        if self.verbose and key in ("width", "height"):
                            logger.info(f"Scaling {key} in nested object: {value} * {self.scale_factor}")
                        scaled = value * self.scale_factor
                        # Preserve integer type if original was integer
                        if isinstance(value, int):
                            obj[key] = int(round(scaled))
                        else:
                            obj[key] = scaled
                        if self.verbose and key in ("width", "height"):
                            logger.info(f"Result: {obj[key]}")
                    elif isinstance(value, dict) and "value" in value:
                        # Handle wrapped values
                        if isinstance(value["value"], (int, float)):
                            scaled = value["value"] * self.scale_factor
                            # Preserve integer type if original was integer
                            if isinstance(value["value"], int):
                                value["value"] = int(round(scaled))
                            else:
                                value["value"] = scaled
                
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    self._scale_recursive(value, key)
        
        elif isinstance(obj, list):
            for item in obj:
                self._scale_recursive(item, parent_key)