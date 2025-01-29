#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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
#   limitations under the License.
import ast
import re
from typing import Optional

import h5py
import numpy as np
import pandas as pd
from scipy.io import whosmat


def find_last_valid_iteration(data_array: np.ndarray):
    """Find last valid iteration across all relevant parameters.

    Parameters
    ----------

    data_array: np.ndarray
        MINFLUX NumPy array.
    """

    # Initialize output
    last_valid = {
        "efo_index": -1,
        "cfr_index": -1,
        "dcr_index": -1,
        "eco_index": -1,
        "loc_index": -1,
        "valid_cfr": [],
    }

    # Number of iterations
    num_iterations = data_array["itr"].shape[1]

    # Do we have aggregated measurements?
    if num_iterations == 1:
        # For clarity, let's set the indices to 0
        last_valid = {
            "efo_index": 0,
            "cfr_index": 0,
            "dcr_index": 0,
            "eco_index": 0,
            "loc_index": 0,
            "valid_cfr": [True],
            "reloc": [False],
        }
        return last_valid

    # Set efo index
    last_valid["efo_index"] = num_iterations - 1

    # Set cfr index
    last_valid["valid_cfr"] = (np.std(data_array["itr"]["cfr"], axis=0) > 0.0).tolist()
    valid_indices = np.where(last_valid["valid_cfr"])[0]
    if len(valid_indices) == 0:
        last_valid["cfr_index"] = num_iterations - 1
    else:
        last_valid["cfr_index"] = valid_indices[-1]

    # Set relocalized iterations: here we can use a simple trick to understand
    # which iterations re-localize. If the second localization of the first TID
    # with more than one is NaN, the iteration does not relocalize, otherwise
    # it does.

    # Is the first trace longer than two localizations?
    reloc_index = None
    if data_array["tid"][1] == data_array["tid"][0]:
        reloc_index = 1
    else:
        u_tids = np.unique(data_array["tid"])
        for i, u_tid in enumerate(u_tids):
            if i == 0:
                # We already know that this tid only has one localization
                continue
            (indices,) = np.where(data_array["tid"] == u_tid)
            if len(indices) < 2:
                continue
            if data_array["tid"][indices[1]] == data_array["tid"][indices[0]]:
                # Found valid index
                reloc_index = indices[1]
                break
    if reloc_index is None:
        # The whole dataset does not contain any iteration with more than one localization
        last_valid["reloc"] = [False] * num_iterations
    else:
        last_valid["reloc"] = np.logical_not(
            np.isnan(data_array["itr"]["loc"][reloc_index, :, 0])
        )

    # Set dcr index
    last_valid["dcr_index"] = num_iterations - 1

    # Set eco index
    last_valid["eco_index"] = num_iterations - 1

    # Set loc index
    last_valid["loc_index"] = num_iterations - 1

    return last_valid


def find_last_valid_iteration_v2(
    data_full_df: pd.DataFrame, num_iterations: Optional[int] = None
):
    """Find last valid iteration across all relevant parameters.

    Parameters
    ----------

    data_full_df: pd.DataFrame
        Full processed DataFrame.

    num_iterations: int
        Maximum number of iterations per localization. Omit to scan it from the data.
    """

    # Initialize output
    last_valid = {
        "efo_index": -1,
        "cfr_index": -1,
        "dcr_index": -1,
        "eco_index": -1,
        "loc_index": -1,
        "valid_cfr": [],
    }

    # Number of iterations
    if num_iterations is None:
        num_iterations = int(np.max(data_full_df["itr"]) + 1)
    num_iterations = int(num_iterations)

    # Do we have aggregated measurements?
    if num_iterations == 1:
        # For clarity, let's set the indices to 0
        last_valid = {
            "efo_index": 0,
            "cfr_index": 0,
            "dcr_index": 0,
            "eco_index": 0,
            "loc_index": 0,
            "valid_cfr": [True],
            "reloc": [False],
        }
        return last_valid

    # Extract trace starting indices
    (trace_start,) = np.where(data_full_df["bot"].to_numpy())

    # Set cfr index
    offsets = np.arange(num_iterations)[:, np.newaxis]
    indices = trace_start + offsets
    cfr = data_full_df["cfr"].to_numpy()[indices]
    last_valid["valid_cfr"] = (np.std(cfr, axis=1) > 0.0).tolist()
    valid_indices = np.where(last_valid["valid_cfr"])[0]
    if len(valid_indices) == 0:
        last_valid["cfr_index"] = num_iterations - 1
    else:
        last_valid["cfr_index"] = valid_indices[-1]

    # Set efo index
    last_valid["efo_index"] = num_iterations - 1

    # Find indices (values) of relocalized iterations (from the first complete iteration)
    (complete_iterations,) = np.where(np.diff(trace_start) > num_iterations)
    if len(complete_iterations) == 0:
        raise ValueError("No complete iterations found!")
    first_complete_iteration = complete_iterations[0]

    candidates = data_full_df["itr"].to_numpy()[
        trace_start[first_complete_iteration] : trace_start[
            first_complete_iteration + 1
        ]
    ]
    candidates = candidates[num_iterations:]
    reloc = np.unique(candidates)
    last_valid["reloc"] = np.array([False] * num_iterations)
    last_valid["reloc"][reloc] = True
    last_valid["reloc"] = last_valid["reloc"].tolist()

    # Set dcr index
    last_valid["dcr_index"] = num_iterations - 1

    # Set eco index
    last_valid["eco_index"] = num_iterations - 1

    # Set loc index
    last_valid["loc_index"] = num_iterations - 1

    return last_valid


def get_reader_version_for_npy_file(file_path):
    """Return version of MinFluxReader required to open this Imspector .npy file without loading it.


    filename: Union[Path, str]
        Full path to the `.npy` file to scan.

    Returns
    -------

    reader_version: int
        Return the version for the MinFluxReader version needed to open this Imspector *.npy file.
    """
    with open(file_path, "rb") as f:
        # Read the magic string
        magic_string = f.read(6)

        if not magic_string == b"\x93NUMPY":
            raise ValueError(f"{file_path} is not a valid .npy file.")

        # Set file pointer at the beginning of the header
        f.seek(8)

        # Manual header parsing, since `np.lib.format.read_array_header_{1|2}_0` seems to find
        # issues with the header structure (at least in some files)
        header_length = int.from_bytes(f.read(2), byteorder="little")
        header_bytes = f.read(header_length)

        try:
            # Try decoding header manually
            header_str = header_bytes.decode("ascii")

            # Basic validation of header string
            header_str = header_str.replace("\n", "").replace(" ", "")

            # Use ast.literal_eval to safely parse
            header_dict = ast.literal_eval(header_str)

        except Exception as parse_error:
            print(f"Manual parsing failed: {parse_error}")
            raise

    # Process header dictionary
    reader_version = 1
    for dtype in header_dict["descr"]:
        if (
            dtype[0] == "fnl"
            or dtype[0] == "bot"
            or dtype[0] == "eot"
            or (dtype[0] == "itr" and dtype[1] == "<i4")
        ):
            reader_version = 2
            break

    return reader_version


def get_reader_version_for_mat_file(file_path):
    """Return version of MinFluxReader required to open this Imspector .mat file without loading it.


    filename: Union[Path, str]
        Full path to the `.mat` file to scan.

    Returns
    -------

    reader_version: int
        Return the version for the MinFluxReader version needed to open this Imspector *.mat file.
    """

    # Returns a list of tuples: (variable name, shape, dtype)
    mat_metadata = whosmat(file_path)

    # Process the list
    reader_version = 1
    for variables in mat_metadata:
        if (
            variables[0] == "fnl"
            or variables[0] == "bot"
            or variables[0] == "eot"
            or (variables[0] == "itr" and variables[1] == "int32")
        ):
            reader_version = 2
            break

    return reader_version


def get_reader_version_for_pmx_file(file_path):
    """Return version of MinFluxReader required to open this .pmx file without loading it.


    filename: Union[Path, str]
        Full path to the `.pmx` file to scan.

    Returns
    -------

    reader_version: int
        Return the version for the MinFluxReader version needed to open this *.pmx file.
    """
    # Open the file and read the data
    with h5py.File(file_path, "r") as f:

        # Read the file_version attribute
        file_version = f.attrs["file_version"]

        if file_version not in ["1.0", "2.0", "3.0"]:
            raise ValueError("Unsupported file version.")

        if file_version in ["1.0", "2.0"]:
            return 1
        else:
            return 2


def version_str_to_int(version_string: str) -> int:
    """Convert version string in the form MAJOR.MINOR(.PATCH) to int for comparisons."""

    version_pattern = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?$")

    match = version_pattern.match(version_string)
    if not match:
        raise ValueError(f"Invalid version string format: {version_string}")
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3)) if match.group(3) else 0
    return major * 10000 + minor * 100 + patch
