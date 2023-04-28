#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
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
#

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from scipy.io import loadmat


class MinFluxReader:
    __slots__ = [
        "__filename",
        "__valid",
        "__scaling_factor",
        "__data_array",
        "__data_df",
        "__data_full_df",
        "__valid_entries",
        "__is_3d",
        "__is_aggregated",
        "__reps",
        "__efo_index",
        "__cfr_index",
        "__eco_index",
        "__dcr_index",
        "__loc_index",
        "__tid_index",
        "__tim_index",
        "__vld_index",
    ]

    def __init__(
        self,
        filename: Union[Path, str],
        valid: bool = True,
        scaling_factor: float = 1e9,
    ):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the .npy file to read

        valid: bool (optional, default = True)
            Whether to load only valid localizations.

        scaling_factor: float (optional, default = 1e9)
            Measurement are stored in meters, and by default they are
            scaled to be in nanometers.
        """

        # Store the filename
        self.__filename: Path = Path(filename)
        if not self.__filename.is_file():
            raise IOError(f"The file {self.__filename} does not seem to exist.")

        # Store the valid flag
        self.__valid: bool = valid

        # Store the scaling factor
        self.__scaling_factor: float = scaling_factor

        # Initialize the data
        self.__data_array = None
        self.__data_df = None
        self.__data_full_df = None
        self.__valid_entries = None

        # Whether the acquisition is 2D or 3D
        self.__is_3d: bool = False

        # Whether the file contains aggregate measurements
        self.__is_aggregated: bool = False

        # Indices dependent on 2D or 3D acquisition
        self.__reps: int = -1
        self.__efo_index: int = -1
        self.__cfr_index: int = -1
        self.__dcr_index: int = -1
        self.__eco_index: int = -1
        self.__loc_index: int = -1

        # Constant indices
        self.__tid_index: int = 0
        self.__tim_index: int = 0
        self.__vld_index: int = 0

        # Load the file
        self._load()

    @property
    def is_3d(self):
        """Returns True is the acquisition is 3D, False otherwise."""
        return self.__is_3d

    @property
    def is_aggregated(self):
        """Returns True is the acquisition is aggregated, False otherwise."""
        return self.__is_aggregated

    @property
    def num_valid_entries(self):
        """Number of valid entries."""
        if self.__data_array is None:
            return 0
        return self.__valid_entries.sum()

    @property
    def num_invalid_entries(self):
        """Number of valid entries."""
        if self.__data_array is None:
            return 0
        return np.logical_not(self.__valid_entries).sum()

    @property
    def valid_raw_data(self) -> Union[None, np.ndarray]:
        """Return the raw data."""
        if self.__data_array is None:
            return None
        return self.__data_array[self.__valid_entries].copy()

    @property
    def processed_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as dataframe (some properties only)."""
        if self.__data_df is not None:
            return self.__data_df

        self.__data_df = self._process()
        return self.__data_df

    @property
    def raw_data_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as dataframe (some properties only)."""
        if self.__data_full_df is not None:
            return self.__data_full_df
        self.__data_full_df = self._raw_data_to_full_dataframe()
        return self.__data_full_df

    @classmethod
    def processed_properties(cls):
        """Returns the properties read from the file that correspond to the processed dataframe column names."""
        return [
            "tid",
            "tim",
            "x",
            "y",
            "z",
            "efo",
            "cfr",
            "eco",
            "dcr",
            "dwell",
            "fluo",
        ]

    @classmethod
    def raw_properties(cls):
        """Returns the properties read from the file and dynamic that correspond to the raw dataframe column names."""
        return ["tid", "aid", "vld", "tim", "x", "y", "z", "efo", "cfr", "eco", "dcr"]

    def _load(self) -> bool:
        """Load the file."""

        if not self.__filename.is_file():
            print(f"File {self.__filename} does not exist.")
            return False

        # Call the specialized _load_*() function
        if self.__filename.name.lower().endswith(".npy"):
            try:
                data_array = np.load(str(self.__filename))
                if "fluo" in data_array.dtype.names:
                    self.__data_array = data_array
                else:
                    self.__data_array = self._migrate_npy_array(data_array)
            except ValueError as e:
                print(f"Could not open {self.__filename}: {e}")
                return False

        elif self.__filename.name.lower().endswith(".mat"):
            try:
                self.__data_array = self._convert_from_mat()
            except ValueError as e:
                print(f"Could not open {self.__filename}: {e}")
                return False
        else:
            print(f"Unexpected file {self.__filename}.")
            return False

        # Store a logical array with the valid entries
        self.__valid_entries = self.__data_array["vld"]

        # Cache whether the data is 2D or 3D and whether is aggregated
        num_locs = self.__data_array["itr"].shape[1]
        if num_locs == 10:
            self.__is_aggregated = False
            self.__is_3d = True
        elif num_locs == 5:
            self.__is_aggregated = False
            self.__is_3d = False
        elif num_locs == 1:
            self.__is_aggregated = True
            self.__is_3d = np.nanmean(self.__data_array["itr"]["loc"][:, :, 2]) != 0.0
        else:
            print(f"Unexpected number of localizations per trace ({num_locs}).")
            return False

        # Set all relevant indices
        self._set_all_indices()

        # Return success
        return True

    def _convert_from_mat(self) -> Union[np.ndarray, None]:
        """Load the MAT file."""

        try:
            mat_array = loadmat(str(self.__filename))
        except ValueError as e:
            print(f"Could not open {self.__filename}: {e}")
            return None

        # Number of entries
        n_entries = len(mat_array["itr"]["itr"][0][0])

        # Number of iterations
        n_iters = mat_array["itr"]["itr"][0][0].shape[-1]

        # Initialize an empty structure NumPy data array
        data_array = self.create_empty_data_array(n_entries, n_iters)

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

        # Return success
        return data_array

    def _process(self) -> Union[None, pd.DataFrame]:
        """Returns processed dataframe for valid (or invalid) entries.

        Returns
        -------

        df: pd.DataFrame
            Processed data as DataFrame.
        """

        # Do we have a data array to work on?
        if self.__data_array is None:
            return None

        if self.__valid:
            indices = self.__valid_entries
        else:
            indices = np.logical_not(self.__valid_entries)

        # Extract the valid iterations
        itr = self.__data_array["itr"][indices]

        # Extract the valid identifiers
        tid = self.__data_array["tid"][indices]

        # Extract the valid time points
        tim = self.__data_array["tim"][indices]

        # Extract the fluorophore IDs
        fluo = self.__data_array["fluo"][indices]
        if np.all(fluo) == 0:
            fluo = np.ones(fluo.shape, dtype=fluo.dtype)

        # The following extraction pattern will change whether the
        # acquisition is normal or aggregated
        if self.is_aggregated:
            # Extract the locations
            loc = itr["loc"].squeeze()

            # Extract EFO
            efo = itr["efo"]

            # Extract CFR
            cfr = itr["cfr"]

            # Extract ECO
            eco = itr["eco"]

            # Extract DCR
            dcr = itr["dcr"]

            # Dwell
            dwell = np.around(eco / (efo / 1000.0), decimals=0)

        else:
            # Extract the locations
            loc = itr[:, self.__loc_index]["loc"] * self.__scaling_factor

            # Extract EFO
            efo = itr[:, self.__efo_index]["efo"]

            # Extract CFR
            cfr = itr[:, self.__cfr_index]["cfr"]

            # Extract ECO
            eco = itr[:, self.__eco_index]["eco"]

            # Extract DCR
            dcr = itr[:, self.__dcr_index]["dcr"]

            # Calculate dwell
            dwell = np.around(eco / (efo / 1000.0), decimals=0)

        # Create a Pandas dataframe for the results
        df = pd.DataFrame(
            index=pd.RangeIndex(start=0, stop=len(tid)),
            columns=MinFluxReader.processed_properties(),
        )

        # Store the extracted valid hits into the dataframe
        df["tid"] = tid
        df["x"] = loc[:, 0]
        df["y"] = loc[:, 1]
        df["z"] = loc[:, 2]
        df["tim"] = tim
        df["efo"] = efo
        df["cfr"] = cfr
        df["eco"] = eco
        df["dcr"] = dcr
        df["dwell"] = dwell
        df["fluo"] = fluo

        return df

    def _raw_data_to_full_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return raw data arranged into a dataframe."""
        if self.__data_array is None:
            return None

        # Intialize output dataframe
        df = pd.DataFrame(columns=MinFluxReader.raw_properties())

        # Allocate space for the columns
        n_rows = len(self.__data_array) * self.__reps

        # Get all unique TIDs and their counts
        _, tid_counts = np.unique(self.__data_array["tid"], return_counts=True)

        # Get all tids (repeated over the repetitions)
        tid = np.repeat(self.__data_array["tid"], self.__reps)

        # Create virtual IDs to mark the measurements of repeated tids
        # @TODO Optimize this!
        aid = np.zeros((n_rows, 1), dtype=np.int32)
        index = 0
        for c in np.nditer(tid_counts):
            tmp = np.repeat(np.arange(c), self.__reps)
            n = len(tmp)
            aid[index : index + n, 0] = tmp
            index += n

        # Get all valid flags (repeated over the repetitions)
        vld = np.repeat(self.__data_array["vld"], self.__reps)

        # Get all timepoints (repeated over the repetitions)
        tim = np.repeat(self.__data_array["tim"], self.__reps)

        # Get all localizations (reshaped to drop the first dimension)
        loc = (
            self.__data_array["itr"]["loc"].reshape((n_rows, 3)) * self.__scaling_factor
        )

        # Get all efos (reshaped to drop the first dimension)
        efo = self.__data_array["itr"]["efo"].reshape((n_rows, 1))

        # Get all cfrs (reshaped to drop the first dimension)
        cfr = self.__data_array["itr"]["cfr"].reshape((n_rows, 1))

        # Get all ecos (reshaped to drop the first dimension)
        eco = self.__data_array["itr"]["eco"].reshape((n_rows, 1))

        # Get all dcrs (reshaped to drop the first dimension)
        dcr = self.__data_array["itr"]["dcr"].reshape((n_rows, 1))

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
        df["eco"] = eco
        df["dcr"] = dcr

        return df

    def _set_all_indices(self):
        """Set indices of properties to be read."""
        if self.__data_array is None:
            return False

        if self.is_aggregated:
            self.__reps = 1
            self.__efo_index = -1  # Not used
            self.__cfr_index = -1  # Not used
            self.__dcr_index = -1  # Not used
            self.__eco_index = -1  # Not used
            self.__loc_index = -1  # Not used
        else:
            if self.is_3d:
                self.__reps = 10
                self.__efo_index = 9
                self.__cfr_index = 6
                self.__dcr_index = 9
                self.__eco_index = 9
                self.__loc_index = 9
            else:
                self.__reps = 5
                self.__efo_index = 4
                self.__cfr_index = 4
                self.__dcr_index = 4
                self.__eco_index = 4
                self.__loc_index = 4

    def create_empty_data_array(self, n_entries: int, n_iters: int):
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

        if n_iters not in [1, 5, 10]:
            raise ValueError("`n_iters` must be one of 1, 5, 10.")

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
                    ("fluo", "<i1"),
                ]
            ),
        )

    def _migrate_npy_array(self, data_array):
        """Migrate the raw Imspector NumPy array into a pyMINFLUX raw array."""

        # Initialize the empty target array
        new_array = self.create_empty_data_array(
            len(data_array), data_array["itr"].shape[-1]
        )

        # Copy the data over
        for field_name in data_array.dtype.names:
            new_array[field_name] = data_array[field_name]

        # Return the migrated array
        return new_array

    def __repr__(self):
        """String representation of the object."""
        if self.__data_array is None:
            return "No file loaded."

        str_valid = (
            "all valid"
            if len(self.__data_array) == self.num_valid_entries
            else f"{self.num_valid_entries} valid and {self.num_invalid_entries} non valid"
        )

        str_acq = "3D" if self.is_3d else "2D"
        aggr_str = "aggregated" if self.is_aggregated else "normal"

        return (
            f"File: {self.__filename.name}: "
            f"{str_acq} {aggr_str} acquisition with {len(self.__data_array)} entries ({str_valid})."
        )

    def __str__(self):
        """Human-friendly representation of the object."""
        return self.__repr__()
