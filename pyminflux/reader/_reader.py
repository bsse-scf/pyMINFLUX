from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd


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
        if not self._filename.is_file():
            raise IOError(f"The file {self._filename} does not seem to exist.")

        # Store the valid flag
        self._valid = valid

        # Initialize the data
        self._data_array = None
        self._data_df = None
        self._data_df_stats = None
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

        # Load the file
        self._load()

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
    def processed_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as dataframe (some properties only)."""
        if self._data_df is not None:
            return self._data_df

        self._data_df = self._process()
        return self._data_df

    @property
    def processed_dataframe_stats(self) -> Union[None, pd.DataFrame]:
        """Return some status on the processed dataframe (some properties only)."""
        if self._data_df_stats is not None:
            return self._data_df_stats
        self._data_df_stats = self._calculate_statistics()
        return self._data_df_stats

    @property
    def raw_data_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as dataframe (some properties only)."""
        if self._data_full_df is not None:
            return self._data_full_df
        self._data_full_df = self._raw_data_to_full_dataframe()
        return self._data_full_df

    def _load(self) -> bool:
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
        """Convert (if needed) and save the full raw dataframe to disk.

        Note: these are the exported dataframe columns:

        "tid", "aid", "vld", "tim", "x", "y", "z", "efo", "cfr", "dcr"
        """

        # Prepare the output file
        out_dir = Path(out_file).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # This will create the dataframe if needed
        df = self.raw_data_dataframe

        # Save
        df.to_csv(out_file, index=False, header=True, na_rep="nan", encoding="utf-8")

    def _process(self) -> Union[None, pd.DataFrame]:
        """Returns processed dataframe for valid (or invalid) entries.

        Returns
        -------

        df: pd.DataFrame
            Processed data as DataFrame.
        """

        # Do we have a data array to work on?
        if self._data_array is None:
            return None

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

        # Create a Pandas dataframe for the results
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

        # Store the extracted valid hits into the dataframe
        df["tid"] = tid
        df["x"] = loc[:, 0]
        df["y"] = loc[:, 1]
        df["z"] = loc[:, 2]
        df["tim"] = tim
        df["efo"] = efo
        df["cfr"] = cfr
        df["dcr"] = dcr

        return df

    def _calculate_statistics(self):
        """Calculate per-trace statistics."""

        # Make sure we have processed dataframe to work on
        if self.processed_dataframe is None:
            return

        # Calculate some statistics per TID on the processed dataframe
        df_grouped = self._data_df.groupby("tid")

        tid = df_grouped["tid"].first().values
        n = df_grouped["tid"].count().values
        mx = df_grouped["x"].mean().values
        my = df_grouped["y"].mean().values
        mz = df_grouped["z"].mean().values
        sx = df_grouped["x"].std().values
        sy = df_grouped["y"].std().values
        sz = df_grouped["z"].std().values

        # Prepare a dataframe with the statistics
        df_tid = pd.DataFrame(columns=["tid", "n", "mx", "my", "mz", "sx", "sy", "sz"])

        df_tid["tid"] = tid
        df_tid["n"] = n
        df_tid["mx"] = mx
        df_tid["my"] = my
        df_tid["mz"] = mz
        df_tid["sx"] = sx
        df_tid["sy"] = sy
        df_tid["sz"] = sz

        # sx, sy sz columns will contain np.nan is n == 1: we replace with 0.0
        df_tid[["sx", "sy", "sz"]] = df_tid[["sx", "sy", "sz"]].fillna(value=0.0)

        return df_tid

    def _raw_data_to_full_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return raw data arranged into a dataframe."""
        if self._data_array is None:
            return None

        # Intialize output dataframe
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

        # Get all unique TIDs and their counts
        _, tid_counts = np.unique(self._data_array["tid"], return_counts=True)

        # Get all tids (repeated over the repetitions)
        tid = np.repeat(self._data_array["tid"], self._reps)

        # Create virtual IDs to mark the measurements of repeated tids
        # @TODO Optimize this!
        aid = np.zeros((n_rows, 1), dtype=np.int32)
        index = 0
        for c in np.nditer(tid_counts):
            tmp = np.repeat(np.arange(c), self._reps)
            n = len(tmp)
            aid[index : index + n, 0] = tmp
            index += n

        # Get all valid flags (repeated over the repetitions)
        vld = np.repeat(self._data_array["vld"], self._reps)

        # Get all timepoints (repeated over the repetitions)
        tim = np.repeat(self._data_array["tim"], self._reps)

        # Get all localizations (reshaped to drop the first dimension)
        loc = self._data_array["itr"]["loc"].reshape((n_rows, 3))

        # Get all efos (reshaped to drop the first dimension)
        efo = self._data_array["itr"]["efo"].reshape((n_rows, 1))

        # Get all cfrs (reshaped to drop the first dimension)
        cfr = self._data_array["itr"]["cfr"].reshape((n_rows, 1))

        # Get all dcrs (reshaped to drop the first dimension)
        dcr = self._data_array["itr"]["dcr"].reshape((n_rows, 1))

        # Build the dataframe
        df["tid"] = tid.astype(np.int32)
        df["aid"] = aid.astype(np.int32)
        df["vld"] = vld
        df["tim"] = tim
        df["x"] = loc[:, 0]
        df["y"] = loc[:, 1]
        df["z"] = loc[:, 2]
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

        return f"File: {self._filename.name}: {str_acq} acquisition with {len(self._data_array)} entries ({str_valid})."

    def __str__(self):
        """Human-friendly representation of the object."""
        return self.__repr__()
