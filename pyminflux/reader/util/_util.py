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
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy.io import loadmat, whosmat


def convert_from_mat(filename: Union[Path, str]) -> Union[np.ndarray, None]:
    """Load MINFLUX MAT file and convert it to MINFLUX NPY array in memory.

    Parameters
    ----------

    filename: Union[Path, str]
        Full path of file to be opened.

    Returns
    -------

    data_array: Union[np.ndarray, None]
        NumPy array if the loading and converting was successful, None otherwise.
    """

    # Load .mat file
    try:
        mat_array = loadmat(str(filename))
    except (FileNotFoundError, ValueError) as e:
        print(f"Could not open {filename}: {e}")
        return None

    # Process it
    try:
        # Number of entries
        n_entries = len(mat_array["itr"]["itr"][0][0])

        # Number of iterations
        n_iters = mat_array["itr"]["itr"][0][0].shape[-1]

        # Initialize an empty structure NumPy data array
        data_array = create_empty_data_array(n_entries, n_iters)

        # Copy the data over
        data_array["vld"] = mat_array["vld"].ravel().astype(data_array.dtype["vld"])
        data_array["sqi"] = mat_array["sqi"].ravel().astype(data_array.dtype["sqi"])
        data_array["gri"] = mat_array["gri"].ravel().astype(data_array.dtype["gri"])
        data_array["tim"] = mat_array["tim"].ravel().astype(data_array.dtype["tim"])
        data_array["tid"] = mat_array["tid"].ravel().astype(data_array.dtype["tid"])
        data_array["act"] = mat_array["act"].ravel().astype(data_array.dtype["act"])
        data_array["dos"] = mat_array["dos"].ravel().astype(data_array.dtype["dos"])
        data_array["sky"] = mat_array["sky"].ravel().astype(data_array.dtype["sky"])
        data_array["itr"]["itr"] = mat_array["itr"]["itr"][0][0].astype(
            data_array["itr"]["itr"].dtype
        )
        data_array["itr"]["tic"] = mat_array["itr"]["tic"][0][0].astype(
            data_array["itr"]["tic"].dtype
        )
        data_array["itr"]["loc"] = mat_array["itr"]["loc"][0][0].astype(
            data_array["itr"]["loc"].dtype
        )
        data_array["itr"]["lnc"] = mat_array["itr"]["lnc"][0][0].astype(
            data_array["itr"]["lnc"].dtype
        )
        data_array["itr"]["eco"] = mat_array["itr"]["eco"][0][0].astype(
            data_array["itr"]["eco"].dtype
        )
        data_array["itr"]["ecc"] = mat_array["itr"]["ecc"][0][0].astype(
            data_array["itr"]["ecc"].dtype
        )
        data_array["itr"]["efo"] = mat_array["itr"]["efo"][0][0].astype(
            data_array["itr"]["efo"].dtype
        )
        data_array["itr"]["efc"] = mat_array["itr"]["efc"][0][0].astype(
            data_array["itr"]["efc"].dtype
        )
        data_array["itr"]["sta"] = mat_array["itr"]["sta"][0][0].astype(
            data_array["itr"]["sta"].dtype
        )
        data_array["itr"]["cfr"] = mat_array["itr"]["cfr"][0][0].astype(
            data_array["itr"]["cfr"].dtype
        )
        data_array["itr"]["dcr"] = mat_array["itr"]["dcr"][0][0].astype(
            data_array["itr"]["dcr"].dtype
        )
        data_array["itr"]["ext"] = mat_array["itr"]["ext"][0][0].astype(
            data_array["itr"]["ext"].dtype
        )
        data_array["itr"]["gvy"] = mat_array["itr"]["gvy"][0][0].astype(
            data_array["itr"]["gvy"].dtype
        )
        data_array["itr"]["gvx"] = mat_array["itr"]["gvx"][0][0].astype(
            data_array["itr"]["gvx"].dtype
        )
        data_array["itr"]["eoy"] = mat_array["itr"]["eoy"][0][0].astype(
            data_array["itr"]["eoy"].dtype
        )
        data_array["itr"]["eox"] = mat_array["itr"]["eox"][0][0].astype(
            data_array["itr"]["eox"].dtype
        )
        data_array["itr"]["dmz"] = mat_array["itr"]["dmz"][0][0].astype(
            data_array["itr"]["dmz"].dtype
        )
        data_array["itr"]["lcy"] = mat_array["itr"]["lcy"][0][0].astype(
            data_array["itr"]["lcy"].dtype
        )
        data_array["itr"]["lcx"] = mat_array["itr"]["lcx"][0][0].astype(
            data_array["itr"]["lcx"].dtype
        )
        data_array["itr"]["lcz"] = mat_array["itr"]["lcz"][0][0].astype(
            data_array["itr"]["lcz"].dtype
        )
        data_array["itr"]["fbg"] = mat_array["itr"]["fbg"][0][0].astype(
            data_array["itr"]["fbg"].dtype
        )

    except KeyError as k:
        print(f"Error processing file array: could not find key {k}.")
        data_array = None

    except Exception as e:
        print(f"Error processing file array: unexpected structure.")
        data_array = None

    # Return success
    return data_array


def create_empty_data_array(n_entries: int, n_iters: int) -> np.ndarray:
    """Initializes a structured data array compatible with those exported from Imspector.

    Parameters
    ----------

    n_entries: int
        Number of localizations in the array.

    n_iters: int
        Number of iterations per localization.
        10 for 3D datasets, 5 for 2D datasets, 1 for aggregated measurements.

    Returns
    -------

    array: Empty array with the requested dimensionality.
    """

    return np.empty(
        n_entries,
        dtype=np.dtype(
            [
                (
                    "itr",
                    [
                        ("itr", "<i4"),
                        ("tic", "<u8"),
                        ("loc", "<f8", (3,)),
                        ("lnc", "<f8", (3,)),
                        ("eco", "<i4"),
                        ("ecc", "<i4"),
                        ("efo", "<f8"),
                        ("efc", "<f8"),
                        ("sta", "<i4"),
                        ("cfr", "<f8"),
                        ("dcr", "<f8"),
                        ("ext", "<f8", (3,)),
                        ("gvy", "<f8"),
                        ("gvx", "<f8"),
                        ("eoy", "<f8"),
                        ("eox", "<f8"),
                        ("dmz", "<f8"),
                        ("lcy", "<f8"),
                        ("lcx", "<f8"),
                        ("lcz", "<f8"),
                        ("fbg", "<f8"),
                    ],
                    (n_iters,),
                ),
                ("sqi", "<u4"),
                ("gri", "<u4"),
                ("tim", "<f8"),
                ("tid", "<i4"),
                ("vld", "?"),
                ("act", "?"),
                ("dos", "<i4"),
                ("sky", "<i4"),
                ("fluo", "<u1"),
            ]
        ),
    )


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

    # Find indices (values) of relocalized iterations
    candidates = data_full_df["itr"].to_numpy()[trace_start[0] : trace_start[1]]
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


def migrate_npy_array(data_array) -> Union[np.ndarray, None]:
    """Migrate the raw Imspector NumPy array into a pyMINFLUX raw array.

    Parameters
    ----------

    data_array: np.ndarray
        MINFLUX NumPy array.

    Returns
    -------

    new_array: np.ndarray
        Migrated MINFLUX NumPy array (with "fluo" column).
    """

    # Make sure that data_array is not None
    if data_array is None:
        return None

    # Initialize the empty target array
    new_array = create_empty_data_array(len(data_array), data_array["itr"].shape[-1])

    # Copy the data over
    for field_name in data_array.dtype.names:
        if field_name == "itr":
            for itr_field_name in data_array["itr"].dtype.names:
                new_array["itr"][itr_field_name] = data_array["itr"][itr_field_name]
        else:
            new_array[field_name] = data_array[field_name]

    # Make sure to initialize the "fluo" column
    if "fluo" not in data_array.dtype.names:
        new_array["fluo"] = np.uint8(0)

    # Return the migrated array
    return new_array


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
