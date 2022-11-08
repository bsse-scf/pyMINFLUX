from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd


class MinFluxReader:

    def __init__(self, filename: Union[Path, str]):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the .npy file to read
        """

        # Store the filename
        self._filename: Path = Path(filename)

        # Initialize the data
        self._data = None
        self._valid_entries = None

    @property
    def is_3d(self):
        """Returns True is the acquisition is 3D, False otherwise."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return self._data["itr"].shape[1] == 10

    @property
    def loc_index(self):
        """Return the index of the iteration from which to extract the location."""
        return -1

    @property
    def cfr_index(self):
        """Return the index of the iteration from which to extract the CFR."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return 5 if self.is_3d else 2

    @property
    def efo_index(self):
        """Return the index of the iteration from which to extract the EFO."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return 8 if self.is_3d else 3

    @property
    def num_valid_entries(self):
        """Number of valid entries."""
        if self._data is None:
            return 0
        return self._valid_entries.sum()

    @property
    def num_invalid_entries(self):
        """Number of valid entries."""
        if self._data is None:
            return 0
        return len(self._valid_entries) - self._valid_entries.sum()

    @property
    def raw_data(self):
        """Return the raw data."""
        return self._data.copy()

    def load(self) -> bool:
        """Load the file."""

        if not self._filename.is_file():
            print(f"File {self._filename} does not exist.")
            return False

        try:
            self._data = np.load(str(self._filename))
        except ValueError as e:
            print(f"Could not open {self._filename}: {e}")
            return False

        # Store a logical array with the valid entries
        self._valid_entries = self._data["vld"]

        # Return success
        return True

    def process(self, valid: bool = True, scaling_factor: float = 1.0, drop_nan: bool = True) -> pd.DataFrame:
        """Returns processed dataframe for valid (or invalid) entries."""

        if valid:
            indices = self._valid_entries
        else:
            indices = np.logical_not(self._valid_entries)

        # Extract the valid time points
        tim = self._data["tim"][indices]

        # Extract the locations for the valid iterations
        itr = self._data["itr"][indices]
        loc = itr[:, self.loc_index]["loc"]

        # Extract the valid identifiers
        tid = self._data["tid"][indices]

        # Extract EFO
        efo = itr[:, self.efo_index]["efo"]

        # Extract CFR
        cfr = itr[:, self.cfr_index]["cfr"]

        # Create a Pandas dataframe for the results
        df = pd.DataFrame(
            index=pd.RangeIndex(start=0, stop=np.sum(indices)),
            columns=["tid", "x", "y", "z", "tim", "efo", "cfr"]
        )

        # Store the extracted valid hits into the dataframe
        df["tid"] = tid
        df["x"] = loc[:, 0] * scaling_factor
        df["y"] = loc[:, 1] * scaling_factor
        df["z"] = loc[:, 2] * scaling_factor
        df["tim"] = tim
        df["efo"] = efo
        df["cfr"] = cfr

        # Internal control
        num_zero_values = np.sum(df["z"].values == 0.0)
        num_nan_values = np.sum(np.isnan(df["z"].values))
        num_non_null_values = len(df["z"].values) - num_zero_values - num_nan_values
        valid_str = "valid" if valid else "invalid"
        num_dir_str = "3D" if self.is_3d else "2D"

        print(f"This {valid_str} {num_dir_str} dataset has "
              f"{num_zero_values} 0.0 values and {num_nan_values} NaN values "
              f"from a total of {len(df['z'].values)} ({num_non_null_values} non-zero values).")

        if drop_nan:
            print(f"Dropping NaN values.")
            df.dropna(axis=0, how="any", inplace=True)

        return df

    def __repr__(self):
        """String representation of the object."""
        if self._data is None:
            return "No file loaded."

        str_valid = "all valid" \
            if len(self._data) == self.num_valid_entries else \
            f"{self.num_valid_entries} valid and {self.num_invalid_entries} non valid"

        str_acq = "3D" if self.is_3d else "2D"

        return f"File: {self._filename.name}\n" \
               f"Number of entries: {len(self._data)} entries ({str_valid})\n" \
               f"Acquisition: {str_acq}"

    def __str__(self):
        """Human-friendly representation of the object."""
        return self.__repr__()
