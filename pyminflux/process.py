from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd


def get_colors_for_unique_ids(
    ids: Union[pd.Series, np.ndarray], make_unique: bool = False, seed: int = 2021
) -> np.ndarray:
    """Return an Nx3 matrix of RGB colors in the range 0.0 ... 1.0 for all unique ids in `ids`

    @param ids: Union[pd.Series, np.ndarray]
        Series or array of ids, that may contain repetitions.

    @param make_unique: bool
        Set to True to make unique (one row per ID) or False to map a unique
        color to each of the original IDs vector.

    @param seed: int
        Seed of the random generator to make sure that the sequence of colors
        is reproducible.

    @return np.ndarray
        Nx3 matrix of RGB colors in the range 0.0 ... 1.0.
    """

    # Make sure the sequence of colors is preserved across runs
    rng = np.random.default_rng(seed)

    # Get the list of unique IDs
    u_ids = np.unique(ids)

    if make_unique:

        # Allocate the matrix of colors
        colors = np.zeros((len(u_ids), 3), dtype=np.float64)

        for i in range(len(u_ids)):
            colors[i, 0] = rng.random(1)
            colors[i, 1] = rng.random(1)
            colors[i, 2] = rng.random(1)

    else:
        # Allocate the matrix of colors
        colors = np.zeros((len(ids), 3), dtype=np.float64)

        for id in u_ids:
            i = np.where(ids == id)
            colors[i, 0] = rng.random(1)
            colors[i, 1] = rng.random(1)
            colors[i, 2] = rng.random(1)

    return colors


def process_minflux_file(
    filename: Union[Path, str], scaling_factor: float = 1e9, verbose: bool = False
) -> Union[pd.DataFrame, None]:
    """Load the MINFLUX .npy file and extract the valid hits.

    @param filename: Union[Path, str]
        Full path of the .npy file to process.

    @param scaling_factor: float
        Scaling factor for the hit coordinates. Default is 1e9 since the coordinates appear to be
        saved in meters at the resolution of 1 nm.

    @param verbose: bool (Optional, default: False)
        Set to True to display verbose information. Otherwise, the function is silent.

    @return Union[pd.DataFrame, None]
        Pandas dataframe with id, x, y, z coordinates, and timepoint of all valid hits; or None if the file could not be processed.
    """

    if verbose:
        print(f"Reading file: {filename}")

    # Load the .npy file
    try:
        npy_array = np.load(filename)
    except:
        return None

    # Number of entries to process
    n_entries = len(npy_array)

    # Get the valid entries
    valid = npy_array["vld"]

    # Count the valid entries
    n_valid = np.sum(valid)

    if verbose:
        print(f"Found {n_valid} valid hits from a total of {n_entries} entries.")

    # Extract the valid time points
    tim = npy_array["tim"][valid]

    # Extract the locations for the valid iterations
    itr = npy_array["itr"][valid]
    loc = itr[:, itr.shape[1] - 1]["loc"]

    # Extract the valid identifiers
    tid = npy_array["tid"][valid]

    # Create a Pandas dataframe for the results
    hits_df = pd.DataFrame(
        index=pd.RangeIndex(start=0, stop=n_valid),
        columns=["tid", "x", "y", "z", "tim"],
    )

    # Store the extracted valid hits into the dataframe
    hits_df["tid"] = tid
    hits_df["x"] = loc[:, 0] * scaling_factor
    hits_df["y"] = loc[:, 1] * scaling_factor
    hits_df["z"] = loc[:, 2] * scaling_factor
    hits_df["tim"] = tim

    if verbose:
        print(f"Number of unique IDs: {len(np.unique(tid))}")

    return hits_df
