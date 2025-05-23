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


from pathlib import Path
from pickle import UnpicklingError
from typing import Union

import numpy as np
import pandas as pd
from scipy.io import loadmat

from pyminflux.reader._pmx_reader import PMXReader
from pyminflux.reader.util import find_last_valid_iteration


class MinFluxReader:
    __docs__ = "Reader of MINFLUX data in `.pmx`, `.npy` or `.mat` formats and Imspector m2205 files, and `.pmx` version 1.0 - 2.0."

    __slots__ = [
        "_pool_dcr",
        "_cfr_index",
        "_processed_dataframe",
        "_dcr_index",
        "_dwell_time",
        "_eco_index",
        "_efo_index",
        "_filename",
        "_full_raw_data_array",
        "_is_3d",
        "_is_aggregated",
        "_is_last_valid",
        "_is_tracking",
        "_last_valid",
        "_last_valid_cfr",
        "_loc_index",
        "_relocalizations",
        "_reps",
        "_tid_index",
        "_tim_index",
        "_unit_scaling_factor",
        "_valid",
        "_valid_cfr",
        "_valid_entries",
        "_vld_index",
        "_z_scaling_factor",
    ]

    def __init__(
        self,
        filename: Union[Path, str],
        valid: bool = True,
        z_scaling_factor: float = 1.0,
        is_tracking: bool = False,
        pool_dcr: bool = False,
        dwell_time: float = 1.0,
    ):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx`, `.npy` or `.mat` file to read

        valid: bool (optional, default = True)
            Whether to load only valid localizations.

        z_scaling_factor: float (optional, default = 1.0)
            Refractive index mismatch correction factor to apply to the z coordinates.

        is_tracking: bool (optional, default = False)
            Whether the dataset comes from a tracking experiment; otherwise, it is considered as a
            localization experiment.

        pool_dcr: bool (optional, default = False)
            Whether to pool DCR values weighted by the relative ECO of all relocalized iterations.

        dwell_time: float (optional, default 1.0)
            Dwell time in milliseconds.
        """

        # Store the filename
        self._filename: Path = Path(filename)
        if not self._filename.exists():
            raise IOError(f"The file {self._filename} does not seem to exist.")

        # Keep track of whether the chosen sequence is the last valid.
        self._is_last_valid: bool = False

        # Store the valid flag
        self._valid: bool = valid

        # The localizations are stored in meters in the Imspector files and by
        # design also in the `.pmx` format. Here, we scale them to be in nm
        self._unit_scaling_factor: float = 1e9

        # Store the z correction factor
        self._z_scaling_factor: float = z_scaling_factor

        # Store the dwell time
        self._dwell_time = dwell_time

        # Initialize the data
        self._full_raw_data_array = None
        self._processed_dataframe = None
        self._valid_entries = None

        # Whether the acquisition is 2D or 3D
        self._is_3d: bool = False

        # Whether the acquisition is a tracking dataset
        self._is_tracking: bool = is_tracking

        # Whether to pool the dcr values
        self._pool_dcr = pool_dcr

        # Whether the file contains aggregate measurements
        self._is_aggregated: bool = False

        # Indices dependent on 2D or 3D acquisition and whether the
        # data comes from a localization or a tracking experiment.
        self._reps: int = -1
        self._efo_index: int = -1
        self._cfr_index: int = -1
        self._dcr_index: int = -1
        self._eco_index: int = -1
        self._loc_index: int = -1
        self._valid_cfr: list = []
        self._relocalizations: list = []

        # Constant indices
        self._tid_index: int = 0
        self._tim_index: int = 0
        self._vld_index: int = 0

        # Keep track of the last valid global and CFR iterations as returned
        # by the initial scan
        self._last_valid: int = -1
        self._last_valid_cfr: int = -1

        # Load the file
        if not self._load():
            raise IOError(f"The file {self._filename} is not a valid MINFLUX file.")

    @property
    def version(self) -> int:
        return 1

    @property
    def is_last_valid(self) -> Union[bool, None]:
        """Return True if the selected iteration is the "last valid", False otherwise.
        If the dataframe has not been processed yet, `is_last_valid` will be None."""
        if self._processed_dataframe is None:
            return None
        return self._is_last_valid

    @property
    def z_scaling_factor(self) -> float:
        """Returns the scaling factor for the z coordinates."""
        return self._z_scaling_factor

    @property
    def is_3d(self) -> bool:
        """Returns True is the acquisition is 3D, False otherwise."""
        return self._is_3d

    @property
    def is_aggregated(self) -> bool:
        """Returns True is the acquisition is aggregated, False otherwise."""
        return self._is_aggregated

    @property
    def is_tracking(self) -> bool:
        """Returns True for a tracking acquisition, False otherwise."""
        return self._is_tracking

    @property
    def is_pool_dcr(self) -> bool:
        """Returns True if the DCR values over all relocalized iterations (to use all photons)."""
        return self._pool_dcr

    @property
    def dwell_time(self) -> float:
        """Returns the dwell time."""
        return self._dwell_time

    @property
    def num_valid_entries(self) -> int:
        """Number of valid entries."""
        if self._valid_entries is None:
            return 0
        return int(self._valid_entries.sum())

    @property
    def num_invalid_entries(self) -> int:
        """Number of valid entries."""
        if self._valid_entries is None:
            return 0
        return int(np.logical_not(self._valid_entries).sum())

    @property
    def tot_num_entries(self) -> int:
        """Total number of entries."""
        return self.num_valid_entries + self.num_invalid_entries

    @property
    def valid_cfr(self) -> list:
        """Return the iterations with valid CFR measurements.

        Returns
        -------
        cfr: boolean array with True for the iteration indices
             that have a valid measurement.
        """
        if self.tot_num_entries == 0:
            return []
        return self._valid_cfr

    @property
    def relocalizations(self) -> list:
        """Return the iterations with relocalizations.

        Returns
        -------
        reloc: boolean array with True for the iteration indices that are relocalized.
        """
        if self.tot_num_entries == 0:
            return []
        return self._relocalizations

    @property
    def valid_raw_data_array(self) -> Union[None, np.ndarray]:
        """Return the raw data."""
        if self.tot_num_entries == 0:
            return None
        return self._full_raw_data_array[self._valid_entries].copy()

    @property
    def processed_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the raw data as dataframe (some properties only)."""
        if self._processed_dataframe is not None:
            return self._processed_dataframe

        self._processed_dataframe = self._process()
        return self._processed_dataframe

    @property
    def filename(self) -> Union[Path, None]:
        """Return the filename if set."""
        if self._filename is None:
            return None
        return Path(self._filename)

    def set_indices(self, index, cfr_index, process: bool = True):
        """Set the parameter indices.

        We distinguish between the index of all parameters
        that are always measured and are accessed from the
        same iteration, and the cfr index, that is not
        always measured.

        Parameters
        ----------

        index: int
            Global iteration index for all parameters but cfr

        cfr_index: int
            Iteration index for cfr

        process: bool (Optional, default = True)
            By default, when setting the indices, the data is rescanned
            and the dataframe is rebuilt. In case several properties of
            the MinFluxReader are modified sequentially, the processing
            can be disabled and run only once after the last change.
            However, this only applies after the first load/scan, when
            the processed dataframe has not been created yet. If the
            dataframe already exists, this flag will be ignored and the
            processing will take place.
        """

        # The cfr index is not allowed to be smaller than the global iteration index
        if index < cfr_index:
            raise ValueError(
                "The value of index must be greater than or equal to cfr_index."
            )

        # Make sure there is loaded data
        if self.tot_num_entries == 0:
            raise ValueError("No data loaded.")

        if self._reps == -1:
            raise ValueError("No data loaded.")

        if len(self._valid_cfr) == 0:
            raise ValueError("No data loaded.")

        # Check that the arguments are compatible with the loaded data
        if index < 0 or index > self._reps - 1:
            raise ValueError(
                f"The value of index must be between 0 and {self._reps - 1}."
            )

        if cfr_index < 0 or cfr_index > len(self._valid_cfr) - 1:
            raise ValueError(
                f"The value of index must be between 0 and {len(self._valid_cfr) - 1}."
            )

        # Now set the general values
        self._efo_index = index
        self._dcr_index = index
        self._eco_index = index
        self._loc_index = index

        # Set the cfr index
        self._cfr_index = cfr_index

        # Constant indices
        self._tid_index: int = 0
        self._tim_index: int = 0
        self._vld_index: int = 0

        # Re-process the file? If the processed dataframe already exists,
        # the processing will take place anyway.
        if process or self._processed_dataframe is not None:
            self._processed_dataframe = self._process()

    def set_tracking(self, is_tracking: bool, process: bool = True):
        """Sets whether the acquisition is tracking or localization.

        Parameters
        ----------

        is_tracking: bool
            Set to True for a tracking acquisition, False for a localization
            acquisition.

        process: bool (Optional, default = True)
            By default, when setting the tracking flag, the data is rescanned
            and the dataframe is rebuilt. In case several properties of
            the MinFluxReader are modified sequentially, the processing
            can be disabled and run only once after the last change.
            However, this only applies after the first load/scan, when
            the processed dataframe has not been created yet. If the
            dataframe already exists, this flag will be ignored and the
            processing will take place.
        """

        # Update the flag
        self._is_tracking = is_tracking

        # Re-process the file?
        if process or self._processed_dataframe is not None:
            self._processed_dataframe = self._process()

    def set_dwell_time(self, dwell_time: float, process: bool = True):
        """
        Sets the dwell time.

        Parameters
        ----------
        dwell_time: float
            Dwell time.

        process: bool (Optional, default = True)
            By default, when setting the dwell time, the data is rescanned
            and the dataframe is rebuilt. In case several properties of
            the MinFluxReader are modified sequentially, the processing
            can be disabled and run only once after the last change.
            However, this only applies after the first load/scan, when
            the processed dataframe has not been created yet. If the
            dataframe already exists, this flag will be ignored and the
            processing will take place.
        """

        # Update the flag
        self._dwell_time = dwell_time

        # Re-process the file?
        if process or self._processed_dataframe is not None:
            self._processed_dataframe = self._process()

    def set_pool_dcr(self, pool_dcr: bool, process: bool = True):
        """
        Sets whether the DCR values should be pooled (and weighted by ECO).

        Parameters
        ----------
        pool_dcr: bool
            Whether the DCR values should be pooled (and weighted by ECO).

        process: bool (Optional, default = True)
            By default, when setting the DCR binning flag, the data is rescanned
            and the dataframe is rebuilt. In case several properties of
            the MinFluxReader are modified sequentially, the processing
            can be disabled and run only once after the last change.
            However, this only applies after the first load/scan, when
            the processed dataframe has not been created yet. If the
            dataframe already exists, this flag will be ignored and the
            processing will take place.
        """

        # Update the flag
        self._pool_dcr = pool_dcr

        # Re-process the file?
        if process or self._processed_dataframe is not None:
            self._processed_dataframe = self._process()

    @classmethod
    def processed_properties(cls) -> list:
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
            "fbg",
        ]

    @classmethod
    def raw_properties(cls) -> list:
        """Returns the properties read from the file and dynamic that correspond to the raw dataframe column names."""
        return [
            "tid",
            "aid",
            "vld",
            "tim",
            "x",
            "y",
            "z",
            "efo",
            "cfr",
            "eco",
            "dcr",
            "fbg",
        ]

    def _load(self) -> bool:
        """Load the file."""

        if not self._filename.is_file():
            print(f"File {self._filename} does not exist.")
            return False

        # Call the specialized _load_*() function
        if self._filename.name.lower().endswith(".npy"):
            try:
                data_array = np.load(str(self._filename), allow_pickle=False)
                if "fluo" in data_array.dtype.names:
                    self._full_raw_data_array = data_array
                else:
                    self._full_raw_data_array = _migrate_npy_array(data_array)
            except (
                OSError,
                UnpicklingError,
                ValueError,
                EOFError,
                FileNotFoundError,
                TypeError,
                Exception,
            ) as e:
                print(f"Could not open {self._filename}: {e}")
                return False

        elif self._filename.name.lower().endswith(".mat"):
            try:
                self._full_raw_data_array = _convert_from_mat(self._filename)
            except Exception as e:
                print(f"Could not open {self._filename}: {e}")
                return False

        elif self._filename.name.lower().endswith(".pmx"):
            try:
                # Read filtered dataframe
                self._full_raw_data_array = PMXReader.get_array(self._filename)

                if self._full_raw_data_array is None:
                    print(f"Could not open {self._filename}.")
                    return False
            except Exception as e:
                print(f"Could not open {self._filename}: {e}")
                return False

        else:
            print(f"Unexpected file {self._filename}.")
            return False

        # Store a logical array with the valid entries
        self._valid_entries = self._full_raw_data_array["vld"]

        # Cache whether the data is 2D or 3D and whether is aggregated
        # The cases are different for localization vs. tracking experiments
        # num_locs = self._full_raw_data_array["itr"].shape[1]
        self._is_3d = (
            float(np.nanmean(self._full_raw_data_array["itr"][:, -1]["loc"][:, -1]))
            != 0.0
        )

        # Set all relevant indices
        self._set_all_indices()

        # Return success
        return True

    def _process(self) -> Union[None, pd.DataFrame]:
        """Returns processed dataframe for valid (or invalid) entries.

        Returns
        -------

        df: pd.DataFrame
            Processed data as DataFrame.
        """

        # Do we have a data array to work on?
        if self.tot_num_entries == 0:
            return None

        if self._valid:
            indices = self._valid_entries
        else:
            indices = np.logical_not(self._valid_entries)

        # Extract the valid iterations
        itr = self._full_raw_data_array["itr"][indices]

        # Extract the valid identifiers
        tid = self._full_raw_data_array["tid"][indices]

        # Extract the valid time points
        tim = self._full_raw_data_array["tim"][indices]

        # Extract the fluorophore IDs
        fluo = self._full_raw_data_array["fluo"][indices]
        if np.all(fluo) == 0:
            fluo = np.ones(fluo.shape, dtype=fluo.dtype)

        # The following extraction pattern will change whether the
        # acquisition is normal or aggregated
        if self.is_aggregated:
            # Extract the locations
            loc = itr["loc"].squeeze() * self._unit_scaling_factor
            loc[:, 2] = loc[:, 2] * self._z_scaling_factor

            # Extract EFO
            efo = itr["efo"]

            # Extract CFR
            cfr = itr["cfr"]

            # Extract ECO
            eco = itr["eco"]

            # Extract DCR
            dcr = itr["dcr"]

            # Extract the background
            bfg = itr["bfg"]

            # Dwell
            dwell = np.around((eco / (efo / 1000)) / self._dwell_time, decimals=0)

        else:
            # Extract the locations
            loc = itr[:, self._loc_index]["loc"] * self._unit_scaling_factor
            loc[:, 2] = loc[:, 2] * self._z_scaling_factor

            # Extract EFO
            efo = itr[:, self._efo_index]["efo"]

            # Extract CFR
            cfr = itr[:, self._cfr_index]["cfr"]

            # Extract ECO
            eco = itr[:, self._eco_index]["eco"]

            # Extract the background
            fbg = itr[:, self._loc_index]["fbg"]

            # Pool DCR values?
            if self._pool_dcr and np.sum(self._relocalizations) > 1:

                # Calculate ECO contributions
                eco_all = itr[:, self._relocalizations]["eco"]
                eco_sum = eco_all.sum(axis=1)
                eco_all_norm = eco_all / eco_sum.reshape(-1, 1)

                # Extract DCR values and weigh them by the relative ECO contributions
                dcr = itr[:, self._relocalizations]["dcr"]
                dcr = dcr * eco_all_norm
                dcr = dcr.sum(axis=1)

            else:

                # Extract DCR
                dcr = itr[:, self._dcr_index]["dcr"]

            # Calculate dwell
            dwell = np.around((eco / (efo / 1000)) / self._dwell_time, decimals=0)

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
        df["fbg"] = fbg
        df["fluo"] = fluo

        # Remove rows with NaNs in the loc matrix
        df = df.dropna(subset=["x"])

        # Check if the selected indices correspond to the last valid iteration
        self._is_last_valid = bool(
            self._cfr_index == self._last_valid_cfr
            and self._efo_index == self._last_valid
        )

        return df

    def _set_all_indices(self):
        """Set indices of properties to be read."""
        if self.tot_num_entries == 0:
            return False

        # Number of iterations
        self._reps = self._full_raw_data_array["itr"].shape[1]

        # Is this an aggregated acquisition?
        if self._reps == 1:
            self._is_aggregated = True
        else:
            self._is_aggregated = False

        # Query the data to find the last valid iteration
        # for all measurements
        last_valid = find_last_valid_iteration(self._full_raw_data_array)

        # Set the extracted indices
        self._efo_index = last_valid["efo_index"]
        self._cfr_index = last_valid["cfr_index"]
        self._dcr_index = last_valid["dcr_index"]
        self._eco_index = last_valid["eco_index"]
        self._loc_index = last_valid["loc_index"]
        self._valid_cfr = last_valid["valid_cfr"]
        self._relocalizations = last_valid["reloc"]

        # Keep track of the last valid iteration
        self._last_valid = len(self._valid_cfr) - 1
        self._last_valid_cfr = last_valid["cfr_index"]

    def __repr__(self) -> str:
        """String representation of the object."""
        if self.num_valid_entries == 0:
            return "No file loaded."

        str_valid = (
            "all valid"
            if self.num_invalid_entries == 0
            else f"{self.num_valid_entries} valid and {self.num_invalid_entries} non valid"
        )

        str_acq = "3D" if self.is_3d else "2D"
        aggr_str = "aggregated" if self.is_aggregated else "normal"

        return (
            f"File: {self._filename.name}: "
            f"{str_acq} {aggr_str} acquisition with {self.tot_num_entries} entries ({str_valid})."
        )

    def __str__(self) -> str:
        """Human-friendly representation of the object."""
        return self.__repr__()


def _create_empty_data_array(n_entries: int, n_iters: int) -> np.ndarray:
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


def _migrate_npy_array(data_array) -> Union[np.ndarray, None]:
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
    new_array = _create_empty_data_array(len(data_array), data_array["itr"].shape[-1])

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


def _convert_from_mat(filename: Union[Path, str]) -> Union[np.ndarray, None]:
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
        data_array = _create_empty_data_array(n_entries, n_iters)

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
