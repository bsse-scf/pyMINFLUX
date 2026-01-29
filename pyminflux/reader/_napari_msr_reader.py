"""napari reader for MSR (OBF) files, using the existing MSRReader.

This reader exposes a minimal npe2-compatible reader function that returns
napari LayerData tuples for 2D image stacks contained in an MSR file.

It does not modify or depend on the standalone pyMINFLUX GUI.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple, Union

import numpy as np

from ._msr_reader import MSRReader


LayerData = Tuple[np.ndarray, Dict[str, Any], str]


def read_msr(path: Union[str, List[str]]) -> List[LayerData]:
    """Read an MSR file and return a list of napari Image layers.

    Parameters
    ----------
    path : str | list[str]
        Path to a single .msr file. If a list is provided, the first item is used.

    Returns
    -------
    list[LayerData]
        A list of (data, metadata, layer_type) tuples for napari.
    """

    # Support both str and list[str] signatures (napari may pass a list when stacking)
    if isinstance(path, list):
        if not path:
            raise ValueError("No file paths provided to MSR reader.")
        path = path[0]

    reader = MSRReader(path)
    if not reader.scan():
        # If we got here via pattern matching but file is invalid, raise to indicate failure
        raise ValueError(f"File does not appear to be a valid MSR/OBF file: {path}")

    layers: List[LayerData] = []

    for i in range(reader.num_stacks):
        meta = reader[i]
        if meta is None:
            continue

        # Only add 2D images
        if (np.array(meta.num_pixels) > 1).sum() != 2:
            continue

        data = reader.get_data(i)
        if data is None:
            continue

        # Pixel sizes and offsets are returned per axis in order [x, y, ...]
        # Napari expects scale/translate in array axis order (row=y, col=x)
        pixel_sizes = reader.get_data_pixel_sizes(stack_index=i, scaled=True) or []
        offsets = reader.get_data_offsets(stack_index=i, scaled=True) or []

        # Defensive defaults if metadata is incomplete
        sx = float(pixel_sizes[0]) if len(pixel_sizes) > 0 else 1.0
        sy = float(pixel_sizes[1]) if len(pixel_sizes) > 1 else 1.0
        tx = float(offsets[0]) if len(offsets) > 0 else 0.0
        ty = float(offsets[1]) if len(offsets) > 1 else 0.0

        name = meta.stack_name or f"MSR stack {i}"

        layer_meta: Dict[str, Any] = {
            "name": name,
            "scale": (sy, sx),
            "translate": (ty, tx),
        }

        layers.append((data, layer_meta, "image"))

    if not layers:
        # No readable 2D images found
        raise ValueError(
            f"No 2D image stacks found in MSR file: {path}. This reader currently supports 2D images only."
        )

    return layers
