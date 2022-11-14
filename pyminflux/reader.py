import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from pyminflux.processor.processor import process_raw_data_cython


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
        self._data_df = None
        self._valid_entries = None

    @property
    def is_3d(self):
        """Returns True is the acquisition is 3D, False otherwise."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return self._data["itr"].shape[1] == 10

    @property
    def reps(self):
        """Returns the number of repetitions per individual trace."""
        if self._data is None:
            raise ValueError("No data loaded.")
        if self.is_3d:
            return 10
        else:
            return 5

    @property
    def loc_index(self):
        """Return the index of the iteration from which to extract the location."""
        return -1

    @property
    def cfr_index(self):
        """Return the index of the iteration from which to extract the CFR."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return 6 if self.is_3d else 3

    @property
    def dcr_index(self):
        """Return the index of the iteration from which to extract the DCR."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return 9 if self.is_3d else 4

    @property
    def efo_index(self):
        """Return the index of the iteration from which to extract the EFO."""
        if self._data is None:
            raise ValueError("No data loaded.")
        return 9 if self.is_3d else 4

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
    def raw_data(self) -> Union[None, np.ndarray]:
        """Return the raw data."""
        if self._data is None:
            return None
        return self._data.copy()

    @property
    def raw_data_df(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as dataframe."""
        if self._data_df is not None:
            return self._data_df
        self._data_df = self._process_all()
        return self._data_df

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

    def process_id(self, tid: int) -> tuple:
        """Returns dataframe of measurements for given ID.

        Parameters
        ----------

        tid: int
            Id of the trace to process.

        Returns
        -------

        vld: np.ndarray (Nx5) for 2D, (Nx10) for 3D
            Valid flags for the localizations in the trace

        tim: np.ndarray (1xN)
            Timepoints

        loc: np.ndarray (Nx5x3) for 2D, (Nx10x3) for 3D
            Localization coordinates

        n_loc: np.ndarray (Nx1)
            Number of non-NaN localizations per trace

        efo: np.ndarray (Nx5) for 2D, (Nx10) for 3D
            EFO meaurements

        n_efo: np.ndarray (Nx1)
            Number of non-NaN EFO measurements per trace

        cfr: np.ndarray (Nx5) for 2D, (Nx10) for 3D
            CFR meaurements

        n_cfr: np.ndarray (Nx1)
            Number of non-NaN CFR measurements per trace

        dcr: np.ndarray (Nx5) for 2D, (Nx10) for 3D
            DCR meaurements

        n_dcr: np.ndarray (Nx1)
            Number of non-NaN DCR measurements per trace
        """

        data = self._data[self._data["tid"] == tid]
        if len(data) == 0:
            print(f"No trace with ID {tid} found in the data.")
            return None, None, None, None, None, None, None, None, None, None

        # Extract the valid time points
        tim = data["tim"]

        # Extract valid flags for these trace
        vld = data["vld"]

        # Extract the localizations for the valid iterations and
        # count how many valid localizations there are for each trace
        loc = data["itr"]["loc"]
        n_loc = np.logical_not(np.isnan(loc))[:, :, 0].sum(axis=1)

        # Extract EFO
        efo = data["itr"]["efo"]
        n_efo = np.logical_not(np.isnan(efo)).sum(axis=1)

        # Extract CFR
        cfr = data["itr"]["cfr"]
        n_cfr = np.logical_not(np.isnan(cfr)).sum(axis=1)

        # Extract DCR
        dcr = data["itr"]["dcr"]
        n_dcr = np.logical_not(np.isnan(dcr)).sum(axis=1)

        return vld, tim, loc, n_loc, efo, n_efo, cfr, n_cfr, dcr, n_dcr

    def save_full_dataframe(self, out_file: Union[Path, str]):
        """Convert (if needed) and save the full dataframe to disk.

        Note: these are the exported dataframe columns:

        "tid", "aid", "vld", "tim", "x", "y", "z", "efo", "cfr", "dcr"
        """

        # Prepare the output file
        out_dir = Path(out_file).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # This will create the dataframe if needed
        df = self.raw_data_df

        # Save
        df.to_csv(out_file, index=False, header=True, na_rep="nan", encoding="utf-8")

    def process(self, valid: bool = True, drop_nan: bool = True) -> pd.DataFrame:
        """Returns processed dataframe for valid (or invalid) entries.

        **NOTE** This does not currently work correctly!

        Parameters
        ----------

        valid: bool
            Whether to return valid (or invalid) entries. See note below.

        drop_nan: bool
            Whether to drop rows with NaNs from the dataframe.

        **Notes**:

        * Even for traces marked as valid, CFR values seem to only make sense if DCR values are not NaN!

        Returns
        -------

        df: pd.DataFrame
            Processed and filtered data as DataFrame.
        """

        if valid:
            indices = self._valid_entries
        else:
            indices = np.logical_not(self._valid_entries)

        # Extract the valid time points
        tim = self._data["tim"][indices]

        # Extract the localizations for the valid iterations
        itr = self._data["itr"][indices]
        loc = itr[:, self.loc_index]["loc"]

        # Calculate the mean position, its deviation and the count.
        # The following can give warning when loading "invalid" data,
        # hence we put it in a catch_warnings() scope for now.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mean_loc = np.nanmean(itr["loc"], axis=1)
            std_loc = np.nanstd(itr["loc"], axis=1)
            not_nan_loc = np.logical_not(np.isnan(itr["loc"][:, :, 0]))
            valid_loc_count = np.sum(not_nan_loc, axis=1)

        # Extract the valid identifiers
        tid = self._data["tid"][indices]

        # Extract EFO
        efo = itr[:, self.efo_index]["efo"]

        # Extract CFR
        cfr = itr[:, self.cfr_index]["cfr"]

        # Extract DCR
        dcr = itr[:, self.dcr_index]["dcr"]

        # Create a Pandas dataframe for the results
        df = pd.DataFrame(
            index=pd.RangeIndex(start=0, stop=np.sum(indices)),
            columns=[
                "tid",
                "x",
                "y",
                "z",
                "mx",
                "my",
                "mz",
                "sx",
                "sy",
                "sz",
                "nloc",
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
        df["mx"] = mean_loc[:, 0]
        df["my"] = mean_loc[:, 1]
        df["mz"] = mean_loc[:, 2]
        df["sx"] = std_loc[:, 0]
        df["sy"] = std_loc[:, 1]
        df["sz"] = std_loc[:, 2]
        df["nloc"] = valid_loc_count
        df["tim"] = tim
        df["efo"] = efo
        df["cfr"] = cfr
        df["dcr"] = dcr

        # Internal control
        num_zero_values = np.sum(df["z"].values == 0.0)
        num_nan_values = np.sum(np.isnan(df["z"].values))
        num_non_null_values = len(df["z"].values) - num_zero_values - num_nan_values
        valid_str = "valid" if valid else "invalid"
        num_dir_str = "3D" if self.is_3d else "2D"

        print(
            f"This {valid_str} {num_dir_str} dataset has "
            f"{num_zero_values} 0.0 values and {num_nan_values} NaN values "
            f"from a total of {len(df['z'].values)} ({num_non_null_values} non-zero values)."
        )

        if drop_nan:
            print(f"Dropping NaN values.")
            df.dropna(axis=0, how="any", inplace=True)
            df.reset_index(drop=True, inplace=True)

        return df

    def _process_all(self) -> Union[None, pd.DataFrame]:
        """Return raw data arranged into a dataframe."""
        if self._data is None:
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
        n_rows = len(self._data) * self.reps
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
        tids = np.unique(self._data["tid"])

        # Keep track of the index at the beginning of each iteration
        index = 0

        for c_tid in tqdm(tids):

            # Get data for current TID
            data = self._data[self._data["tid"] == c_tid]

            # Build the artificial IDs: one for each of the
            # traces that share the same TID
            c_aid = np.repeat(np.arange(len(data)), self.reps)

            # Keep track of the number of elements that will be added
            # to each column in this iteration
            n_els = len(c_aid)

            # Add the artificial IDs
            aid[index: index + n_els] = c_aid

            # Timepoints
            c_tim = np.repeat(data["tim"], self.reps)
            tim[index: index + n_els] = c_tim

            # Extract valid flags
            c_vld = np.repeat(data["vld"], self.reps)
            vld[index: index + n_els] = c_vld

            # Extract the localizations from the iterations
            internal_index = index
            for c_loc in data["itr"]["loc"]:
                x[internal_index: internal_index + self.reps] = c_loc[:, 0]
                y[internal_index: internal_index + self.reps] = c_loc[:, 1]
                z[internal_index: internal_index + self.reps] = c_loc[:, 2]
                internal_index += self.reps

            # Extract EFO
            internal_index = index
            for c_efo in data["itr"]["efo"]:
                efo[internal_index: internal_index + self.reps] = c_efo
                internal_index += self.reps

            # Extract CFR
            internal_index = index
            for c_cfr in data["itr"]["cfr"]:
                cfr[internal_index: internal_index + self.reps] = c_cfr
                internal_index += self.reps

            # Extract DCR
            internal_index = index
            for c_dcr in data["itr"]["dcr"]:
                dcr[internal_index: internal_index + self.reps] = c_dcr
                internal_index += self.reps

            # Add the tid
            tid[index: index + n_els] = c_tid * np.ones(np.shape(c_aid))

            # Update the starting index
            index += n_els

            assert index <= n_rows

        # Build the dataframe
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

    def process_cython(self):
        """Try running the Cython code."""

        if self._data is None:
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

        # Process tha data array in cython
        tid, aid, vld, tim, x, y, z, efo, cfr, dcr = process_raw_data_cython(self._data, self.is_3d)
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

        # Build the dataframe
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

    def __repr__(self):
        """String representation of the object."""
        if self._data is None:
            return "No file loaded."

        str_valid = (
            "all valid"
            if len(self._data) == self.num_valid_entries
            else f"{self.num_valid_entries} valid and {self.num_invalid_entries} non valid"
        )

        str_acq = "3D" if self.is_3d else "2D"

        return (
            f"File: {self._filename.name}\n"
            f"Number of entries: {len(self._data)} entries ({str_valid})\n"
            f"Acquisition: {str_acq}"
        )

    def __str__(self):
        """Human-friendly representation of the object."""
        return self.__repr__()
