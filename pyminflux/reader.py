import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from pyminflux.processor.processor import process_raw_data_cython


class MinFluxReader:
    def __init__(self, filename: Union[Path, str], valid: bool = True):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the .npy file to read
        """

        # Store the filename
        self._filename: Path = Path(filename)

        # Store the valid flag
        self._valid = valid

        # Initialize the data
        self._data_array = None
        self._data_df = None
        self._data_full_df = None
        self._valid_entries = None

        # Indices dependent on 2D or 3D acquisition
        self._reps: int = -1
        self._efo_index: int = -1
        self._cfr_index: int = -1
        self._dcr_index: int = -1
        self._loc_index: int = -1

        # Constant indices
        self._tid_index: int = 0
        self._tim_index: int = 0
        self._vld_index: int = 0

    @property
    def is_3d(self):
        """Returns True is the acquisition is 3D, False otherwise."""
        if self._data_array is None:
            raise ValueError("No data loaded.")
        return self._data_array["itr"].shape[1] == 10

    @property
    def num_valid_entries(self):
        """Number of valid entries."""
        if self._data_array is None:
            return 0
        return self._valid_entries.sum()

    @property
    def num_invalid_entries(self):
        """Number of valid entries."""
        if self._data_array is None:
            return 0
        return np.logical_not(self._valid_entries).sum()

    @property
    def raw_data(self) -> Union[None, np.ndarray]:
        """Return the raw data."""
        if self._data_array is None:
            return None
        return self._data_array.copy()

    @property
    def processed_data(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as processed_data (some properties only)."""
        if self._data_df is not None:
            return self._data_df
        self._data_df = self._process()
        return self._data_df

    @property
    def raw_data_full_df(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as processed_data (some properties only)."""
        if self._data_full_df is not None:
            return self._data_full_df
        self._data_full_df = self._raw_data_to_full_dataframe()
        return self._data_full_df

    def load(self) -> bool:
        """Load the file."""

        if not self._filename.is_file():
            print(f"File {self._filename} does not exist.")
            return False

        try:
            self._data_array = np.load(str(self._filename))
        except ValueError as e:
            print(f"Could not open {self._filename}: {e}")
            return False

        # Store a logical array with the valid entries
        self._valid_entries = self._data_array["vld"]

        # Set all relevant indices
        self._set_all_indices()

        # Return success
        return True

    def save_raw_data_full_dataframe(self, out_file: Union[Path, str]):
        """Convert (if needed) and save the full processed_data to disk.

        Note: these are the exported processed_data columns:

        "tid", "aid", "vld", "tim", "x", "y", "z", "efo", "cfr", "dcr"
        """

        # Prepare the output file
        out_dir = Path(out_file).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # This will create the processed_data if needed
        df = self.raw_data_full_df

        # Save
        df.to_csv(out_file, index=False, header=True, na_rep="nan", encoding="utf-8")

    def _process(self) -> pd.DataFrame:
        """Returns processed processed_data for valid (or invalid) entries.

        Returns
        -------

        df: pd.DataFrame
            Processed data as DataFrame.
        """

        if self._valid:
            indices = self._valid_entries
        else:
            indices = np.logical_not(self._valid_entries)

        # Extract the valid iterations
        itr = self._data_array["itr"][indices]

        # Extract the valid identifiers
        tid = self._data_array["tid"][indices]

        # Extract the valid time points
        tim = self._data_array["tim"][indices]

        # Extract the locations
        loc = itr[:, self._loc_index]["loc"]

        # Extract EFO
        efo = itr[:, self._efo_index]["efo"]

        # Extract CFR
        cfr = itr[:, self._cfr_index]["cfr"]

        # Extract DCR
        dcr = itr[:, self._dcr_index]["dcr"]

        # Create a Pandas processed_data for the results
        df = pd.DataFrame(
            index=pd.RangeIndex(start=0, stop=len(tid)),
            columns=[
                "tid",
                "x",
                "y",
                "z",
                "tim",
                "efo",
                "cfr",
                "dcr",
            ],
        )

        # Store the extracted valid hits into the processed_data
        df["tid"] = tid
        df["x"] = loc[:, 0]
        df["y"] = loc[:, 1]
        df["z"] = loc[:, 2]
        df["tim"] = tim
        df["efo"] = efo
        df["cfr"] = cfr
        df["dcr"] = dcr

        return df

    def describe(self):
        """Calculate per-trace statistics."""
        if self._data_df is None:
            return None
        print("Implement me!")

    def _raw_data_to_full_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return raw data arranged into a processed_data."""
        if self._data_array is None:
            return None

        # Intialize output processed_data
        df = pd.DataFrame(
            columns=[
                "tid",
                "aid",
                "vld",
                "tim",
                "x",
                "y",
                "z",
                "efo",
                "cfr",
                "dcr",
            ],
        )

        # Allocate space for the columns
        n_rows = len(self._data_array) * self._reps
        tid = np.empty(shape=(n_rows, ), dtype=np.int32)
        aid = np.empty(shape=(n_rows, ), dtype=np.int32)
        vld = np.empty(shape=(n_rows, ), dtype=bool)
        tim = np.empty(shape=(n_rows, ), dtype=float)
        x = np.empty(shape=(n_rows, ), dtype=float)
        y = np.empty(shape=(n_rows, ), dtype=float)
        z = np.empty(shape=(n_rows, ), dtype=float)
        efo = np.empty(shape=(n_rows, ), dtype=float)
        cfr = np.empty(shape=(n_rows, ), dtype=float)
        dcr = np.empty(shape=(n_rows, ), dtype=float)

        # Get all unique TIDs
        tids = np.unique(self._data_array["tid"])

        # Keep track of the index at the beginning of each iteration
        index = 0

        for c_tid in tqdm(tids):

            # Get data for current TID
            data = self._data_array[self._data_array["tid"] == c_tid]

            # Build the artificial IDs: one for each of the
            # traces that share the same TID
            c_aid = np.repeat(np.arange(len(data)), self._reps)

            # Keep track of the number of elements that will be added
            # to each column in this iteration
            n_els = len(c_aid)

            # Add the artificial IDs
            aid[index: index + n_els] = c_aid

            # Timepoints
            c_tim = np.repeat(data["tim"], self._reps)
            tim[index: index + n_els] = c_tim

            # Extract valid flags
            c_vld = np.repeat(data["vld"], self._reps)
            vld[index: index + n_els] = c_vld

            # Extract the localizations from the iterations
            internal_index = index
            for c_loc in data["itr"]["loc"]:
                x[internal_index: internal_index + self._reps] = c_loc[:, 0]
                y[internal_index: internal_index + self._reps] = c_loc[:, 1]
                z[internal_index: internal_index + self._reps] = c_loc[:, 2]
                internal_index += self._reps

            # Extract EFO
            internal_index = index
            for c_efo in data["itr"]["efo"]:
                efo[internal_index: internal_index + self._reps] = c_efo
                internal_index += self._reps

            # Extract CFR
            internal_index = index
            for c_cfr in data["itr"]["cfr"]:
                cfr[internal_index: internal_index + self._reps] = c_cfr
                internal_index += self._reps

            # Extract DCR
            internal_index = index
            for c_dcr in data["itr"]["dcr"]:
                dcr[internal_index: internal_index + self._reps] = c_dcr
                internal_index += self._reps

            # Add the tid
            tid[index: index + n_els] = c_tid * np.ones(np.shape(c_aid))

            # Update the starting index
            index += n_els

            assert index <= n_rows

        # Build the processed_data
        df["tid"] = tid
        df["aid"] = aid
        df["vld"] = vld
        df["tim"] = tim
        df["x"] = x
        df["y"] = y
        df["z"] = z
        df["efo"] = efo
        df["cfr"] = cfr
        df["dcr"] = dcr

        return df

    def _raw_data_to_full_dataframe_cython(self):
        """Try running the Cython code."""

        if self._data_array is None:
            return None

        # Intialize output processed_data
        df = pd.DataFrame(
            columns=[
                "tid",
                "aid",
                "vld",
                "tim",
                "x",
                "y",
                "z",
                "efo",
                "cfr",
                "dcr",
            ],
        )

        # Process tha data array in cython
        tid, aid, vld, tim, x, y, z, efo, cfr, dcr = process_raw_data_cython(self._data_array, self.is_3d)
        tid = np.asarray(tid)
        aid = np.asarray(aid)
        vld = np.asarray(vld, dtype=bool)
        tim = np.asarray(tim)
        x = np.asarray(x)
        y = np.asarray(y)
        z = np.asarray(z)
        efo = np.asarray(efo)
        cfr = np.asarray(cfr)
        dcr = np.asarray(dcr)

        # Build the processed_data
        df["tid"] = tid
        df["aid"] = aid
        df["vld"] = vld
        df["tim"] = tim
        df["x"] = x
        df["y"] = y
        df["z"] = z
        df["efo"] = efo
        df["cfr"] = cfr
        df["dcr"] = dcr

        return df
    def _set_all_indices(self):
        """Set indices of properties to be read."""
        if self._data_array is None:
            return False

        if self.is_3d:
            self._reps: int = 10
            self._efo_index: int = 9
            self._cfr_index: int = 6
            self._dcr_index: int = 9
            self._loc_index: int = 9
        else:
            self._reps: int = 5
            self._efo_index: int = 4
            self._cfr_index: int = 3
            self._dcr_index: int = 4
            self._loc_index: int = 4

    def __repr__(self):
        """String representation of the object."""
        if self._data_array is None:
            return "No file loaded."

        str_valid = (
            "all valid"
            if len(self._data_array) == self.num_valid_entries
            else f"{self.num_valid_entries} valid and {self.num_invalid_entries} non valid"
        )

        str_acq = "3D" if self.is_3d else "2D"

        return (
            f"File: {self._filename.name}\n"
            f"Number of entries: {len(self._data_array)} entries ({str_valid})\n"
            f"Acquisition: {str_acq}"
        )

    def __str__(self):
        """Human-friendly representation of the object."""
        return self.__repr__()
