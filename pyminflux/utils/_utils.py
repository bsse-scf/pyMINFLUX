#  Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from pathlib import Path
from typing import Union

import numpy as np
import requests

import pyminflux


def check_for_updates():
    """Check for pyMINFLUX updates.

    Returns
    -------

    code: int
        Success code:
        -1: something went wrong retrieving version information.
         0: there are no new versions.
         1: there is a new version.
    version: str
        Version on the server (in the format x.y.z). Set if code is 0 or 1.
    error: str
        Error message. Only set if code is -1.
    """

    # Initialize outputs
    code = -1
    version = ""
    error = ""

    # Get the redirect from the latest release URL
    try:
        response = requests.get(
            "https://github.com/bsse-scf/pyMINFLUX/releases/latest",
            allow_redirects=False,
        )

        # This should redirect (status code 301 or 302)
        if response.status_code in (301, 302):
            redirect_url = response.headers["Location"]
        else:
            error = "Could not check for updates!"
            return code, version, error

    except Exception as e:
        # Could not connect at all
        error = "Could not retrieve version information from server!"
        return code, version, error

    # Try retrieving the version string
    match = re.search(r"\b(\d+)\.(\d+)\.(\d+)$", redirect_url)
    if match:
        x, y, z = match.groups()
    else:
        error = "Could not retrieve version information from server!"
        return code, version, error

    # Set the version
    version = f"{x}.{y}.{z}"

    # Transform new version into an integer
    new_version = 10000 * int(x) + 100 * int(y) + int(z)

    # Current version
    parts = pyminflux.__version__.split(".")

    # Make sure that we have three parts
    if len(parts) != 3:
        error = "Could not retrieve current app information!"
        return code, version, error

    # Transform current version into an integer
    current_version = 10000 * int(parts[0]) + 100 * int(parts[1]) + int(parts[2])

    # Now check
    if new_version > current_version:
        code = 1
    else:
        code = 0

    # Return
    return code, version, error


def intersect_2d_ranges(first_range, second_range):
    """Intersect two 1D ranges (min, max) to get the combined results of two consecutive filtering events."""
    out_range = (
        max(first_range[0], second_range[0]),
        min(first_range[1], second_range[1]),
    )
    return out_range


def find_zarr_root(start_path: Union[str, Path]) -> Path:
    """Traverses up the directory tree from a given Zarr path to find the root of the Zarr store.

    Parameters
    ----------

    start_path: start_path: Union[str, Path]
        Path to a group or array within the Zarr store.

    Returns
    -------

    path: Path
        Path to the root of the Zarr store.

    Raises:
        FileNotFoundError: If no Zarr root is found.
    """

    # Start from the passed path
    path = Path(start_path).resolve()

    while path != path.parent:
        zgroup = path / ".zgroup"
        zarray = path / ".zarray"

        # If either of these files exists, this directory might be a Zarr group/array
        if zgroup.exists() or zarray.exists():
            parent = path.parent
            parent_zgroup = parent / ".zgroup"
            parent_zarray = parent / ".zarray"

            # If the parent does not have Zarr metadata, we've found the root
            if not (parent_zgroup.exists() or parent_zarray.exists()):
                return path
            # Else, move one level up
            path = parent
        else:
            # No Zarr metadata here, so we move up
            path = path.parent

    raise FileNotFoundError("No Zarr root found in the directory hierarchy.")


def remove_subarray_occurrences(candidates: np.ndarray, template: np.ndarray):
    """Remove every complete, contiguous occurrence of `template` from the 1‑D NumPy array `candidates`.

    Parameters
    ----------

    candidates: np.ndarray
        1D array of numbers.

    template: np.ndarray
        1D array of numbers. Must be shorter than candidates.

    Returns
    -------

    filtered_candidates: np.ndarray
        A new 1‑D array; the input is not modified.
    """

    # Make sure we are working with NumPy array
    candidates = np.asarray(candidates)
    template = np.asarray(template)

    m = template.size
    if m == 0 or candidates.size < m:
        return candidates.copy()

    # All length‑m windows (view, no copy)
    windows = np.lib.stride_tricks.sliding_window_view(candidates, m)

    # Start positions where the whole window equals the template
    match_starts = np.where(np.all(windows == template, axis=1))[0]
    if match_starts.size == 0:
        return candidates.copy()

    # Indices that belong to any full template occurrence
    delete_idx = (match_starts[:, None] + np.arange(m)).ravel()

    # Boolean mask: keep everything that is *not* in delete_idx
    keep_mask = np.ones(candidates.size, dtype=bool)
    keep_mask[delete_idx] = False

    return candidates[keep_mask]
