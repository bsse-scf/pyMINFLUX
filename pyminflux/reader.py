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
        self.filename: Path = Path(filename)

        # Initialize the data
        self.data = None
        self.valid_entries = None

        # Is the acquisition 3D?
        self.is_3D: bool = False

        # Keep track of last error
        self.last_error: str = ""

    def load(self) -> bool:
        """Load the file."""

        if not self.filename.is_file():
            self.last_error = f"File {self.filename} does not exist."
            return False

        try:
            self.data = np.load(str(self.filename))
        except ValueError as e:
            self.last_error = f"Could not open {self.filename}: {e}"
            return False

        # Store a logical array with the valid entries
        self.valid_entries = self.data["vld"]

        # Return success
        self.last_error = ""
        return True

    def is_3d(self):
        """Returns True is the acquisition is 3D, False otherwise."""
        if self.data is None:
            raise ValueError("No file loaded.")
        return self.data["itr"].shape[1] == 10

    def process(self, valid: bool = True, scaling_factor: float = 1.0) -> pd.DataFrame:
        """Returns processed dataframe for valid (or invalid) entries."""

        if valid:
            indices = self.valid_entries
        else:
            indices = np.logical_not(self.valid_entries)

        # Extract the valid time points
        tim = self.data["tim"][indices]

        # Extract the locations for the valid iterations
        itr = self.data["itr"][indices]
        loc_itr = itr.shape[1] - 1
        loc = itr[:, loc_itr]["loc"]

        # Extract the valid identifiers
        tid = self.data["tid"][indices]

        # Extract EFO
        efo_itr = 8 if self.is_3d() else 3
        efo = itr[:, efo_itr]["efo"]

        # Extract CFR
        cfr_itr = 5 if self.is_3d() else 2
        cfr = itr[:, cfr_itr]["cfr"]

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

        if not self.is_3d():
            if np.any(df["z"].values != 0):
                valid_str = "valid" if valid else "invalid"
                print(f"This 2D dataset seems to have '{valid_str}' z coordinates != 0.0.")

        return df

    def __repr__(self):
        """String representation of the object."""
        if self.data is None:
            return "No file loaded."

        str_valid = "all valid" \
            if len(self.data) == np.sum(self.valid_entries) else \
            f"{np.sum(self.valid_entries)} valid"

        str_acq = "3D" if self.is_3d() else "2D"

        return f"File: {self.filename.name}\n" \
               f"Number of entries: {len(self.data)} entries ({str_valid})\n" \
               f"Acquisition: {str_acq}"

    def __str__(self):
        """Human-friendly representation of the object."""
        return self.__repr__()
