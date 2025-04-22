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
#  limitations under the License.
import json
from json import JSONDecodeError
from pathlib import Path
from pickle import UnpicklingError
from typing import Union

import numpy as np
import pandas as pd
import zarr
from scipy.io import loadmat

# Avoid circular imports
from pyminflux.reader._pmx_reader import PMXReader
from pyminflux.reader._reader import MinFluxReader
from pyminflux.reader.util import find_last_valid_iteration_v2
from pyminflux.utils._utils import find_zarr_root


class MinFluxReaderV2(MinFluxReader):
    """Reader of MINFLUX data in `.npy`, `.mat` and `.json` Imspector m2410 files, and `.pmx` version 0.6.0 and newer."""

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

        # Version 2 does not use the _full_raw_data_array property, but uses the full dataframe instead
        self._full_raw_dataframe = None

        # Store beamline monitoring data is present
        self._mbm = None

        # Call the base constructor
        super().__init__(
            filename=filename,
            valid=valid,
            z_scaling_factor=z_scaling_factor,
            is_tracking=is_tracking,
            pool_dcr=pool_dcr,
            dwell_time=dwell_time,
        )

        # Delete the _full_raw_data_array property from version 1 (version 2 does NOT
        # store the raw data from Imspector, but the processed dataframes that is
        # derived from it).
        del self._full_raw_data_array

    @property
    def version(self) -> int:
        return 2

    @property
    def valid_full_raw_dataframe(self) -> Union[None, np.ndarray]:
        """Return the raw data."""
        if self.tot_num_entries == 0:
            return None
        return self._full_raw_dataframe[self._valid_entries].copy()

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
            "iid",  # Custom: iteration ID
        ]

    def _load(self) -> bool:
        """Load the file."""

        if not self._filename.exists():
            print(f"File {self._filename} does not exist.")
            return False

        raw_dataframe = pd.DataFrame(
            columns=[
                "vld",
                "fnl",
                "bot",
                "eot",
                "sta",
                "tim",
                "tid",
                "gri",
                "thi",
                "sqi",
                "itr",
                "x",
                "y",
                "z",
                "lncx",
                "lncy",
                "lncz",
                "eco",
                "ecc",
                "efo",
                "efc",
                "cfr",
                "dcr",
                "fbg",
                "fluo",  # Custom: fluorophore ID
                "iid",  # Custom: iteration ID
            ]
        )

        # Do we have a  Zarr file?
        if self._filename.is_dir():
            # Create phony file_ext ".zarr" for the following logic
            file_ext = ".zarr"

        else:
            # Determine file type
            file_ext = self._filename.suffix.lower()

        # Call the specialized _load_*() function
        try:
            if file_ext == ".zarr":
                # Load and convert to NumPy
                raw_dataframe = self._load_zarr(raw_dataframe)
            elif file_ext == ".npy":
                raw_dataframe = self._load_numpy(raw_dataframe)
            elif file_ext == ".mat":
                raw_dataframe = self._load_mat(raw_dataframe)
            elif file_ext == ".json":
                raw_dataframe = self._load_json(raw_dataframe)
            elif file_ext == ".pmx":
                raw_dataframe = self._load_pmx(raw_dataframe)
            else:
                print(f"Unexpected file {self._filename}.")
                return False
        except Exception as e:
            print(f"{e}")
            return False

        # Finalize the initialization for all imported file formats
        if file_ext in [".zarr", ".npy", ".mat", ".json"]:

            # Initialize the fluo field
            raw_dataframe["fluo"] = 1

            # **Important**: apply data types **after** creating the dataframe to make sure that
            # data coming from binary types (.npy and .mat) and data coming from text types (.json)
            # generate identical dataframes.
            data_full_df_dtype = {
                "vld": "?",
                "fnl": "?",
                "bot": "?",
                "eot": "?",
                "sta": "u1",
                "tim": "<f8",
                "tid": "<u4",
                "gri": "<u4",
                "thi": "u1",
                "sqi": "u1",
                "itr": "<i4",
                "x": "<f8",
                "y": "<f8",
                "z": "<f8",
                "lncx": "<f8",
                "lncy": "<f8",
                "lncz": "<f8",
                "eco": "<u4",
                "ecc": "<u4",
                "efo": "<f4",
                "efc": "<f4",
                "fbg": "<f4",
                "cfr": "<f2",
                "dcr": "<f2",
                "fluo": "u1",
                "iid": "<u4",
            }

            # Apply the iteration ID
            raw_dataframe["iid"] = raw_dataframe["fnl"].cumsum().shift(fill_value=0) + 1

            # Apply the correct datatypes to the columns
            raw_dataframe = raw_dataframe.astype(data_full_df_dtype)

        # Assign the new dataframe
        self._full_raw_dataframe = raw_dataframe

        # Store a logical array with the valid entries
        self._valid_entries = self._full_raw_dataframe["vld"]

        # Cache whether the data is 2D or 3D and whether is aggregated
        self._is_3d = not np.all(
            np.abs(self._full_raw_dataframe["z"].to_numpy()) < 1e-11
        )

        # Set all relevant indices
        self._set_all_indices()

        # In case of a Zarr file, try loading beamline monitoring data
        if file_ext == ".zarr":
            self._load_mbm()

        # Return success
        return True

    def _load_mbm(self):
        """Load beamline monitoring data if present."""
        # Make sure that self._filename points to the root of the Zarr file
        self._filename = find_zarr_root(self._filename)

        # Initialize dictionary
        mbm_data = {"mbm": {}}

        # Read grd/mbm
        mbm_points = zarr.load(str(self._filename / "grd" / "mbm" / "points"))
        mbm = zarr.load(str(self._filename / "mbm"))
        grd_mbm = zarr.load(str(self._filename / "grd" / "mbm"))
        if mbm_points is None or mbm is None or grd_mbm is None:
            print(f"No beamline monitoring data found in {self._filename}.")
            self._mbm_data = mbm_data
            return

        mbm_gri = grd_mbm.grp.points.attrs["points_by_gri"]
        mbm_neighbourhood = mbm.grp.attrs["neighbourhood"]

        num_beads = 0
        num_used_beads = 0
        for key in mbm_gri:
            bead_name = mbm_gri[key]["name"]
            pts = mbm_points[mbm_points["gri"] == int(key)]
            bead_data = {"bead_name": bead_name, "gri": key, "used": 0, "points": pts}
            if mbm_gri[key]["times_failed_in_row"] < mbm_gri[key]["stickiness"]:
                bead_data["used"] = 1
                num_used_beads += 1
            mbm_data["mbm"][bead_name] = bead_data
            num_beads += 1

        # Store the loaded information
        self._mbm_data = {"mbm_data": mbm_data, "mbm_neighborhood": mbm_neighbourhood}
        print(
            f"Read {num_beads} "
            f"{'beads' if num_beads != 1 else 'bead'} ({num_used_beads} "
            f"used)."
        )

    def _load_zarr(self, df: pd.DataFrame):
        """Load the Zarr file and update the dataframe."""

        # Make sure that self._filename points to the root of the Zarr file
        self._filename = find_zarr_root(self._filename)

        # Path to "mfx"
        filename = self._filename / "mfx"
        if not filename.is_dir():
            print("Could not open the Zarr file.")
            return None

        # Load array
        npy_array = np.array(zarr.load(str(filename)))
        if npy_array is None:
            print("Could not open the Zarr file.")
            return None

        # Fill the dataframe
        for name in npy_array.dtype.names:
            if name == "dcr":
                # In version 2, the dcr is 2D: dcr[:, 0] corresponds to the dcr of
                # version 1, while dcr[:, 1] is just 1.0 - dcr[:, 0]. We drop the
                # second dimension.
                df["dcr"] = npy_array["dcr"][:, 0]
                continue

            # Special cases
            if name == "loc":
                df["x"] = npy_array["loc"][:, 0]
                df["y"] = npy_array["loc"][:, 1]
                df["z"] = npy_array["loc"][:, 2]
                continue

            if name == "lnc":
                df["lncx"] = npy_array["lnc"][:, 0]
                df["lncy"] = npy_array["lnc"][:, 1]
                df["lncz"] = npy_array["lnc"][:, 2]
                continue

            # Single arrays
            df[name] = npy_array[name]

        # Incomplete traces are kept in the Zarr file; we drop them before
        # building the clean dataframe.
        thresh = int(np.max(df["itr"]) + 1)
        tid_counts = df["tid"].value_counts()
        valid_traces = tid_counts[tid_counts >= thresh].index
        df = df[df["tid"].isin(valid_traces)]

        return df

    def _load_numpy(self, df: pd.DataFrame):
        """Load the NumPy file and update the dataframe."""
        try:
            # Load array
            npy_array = np.load(str(self._filename), allow_pickle=False)

        except (
            OSError,
            UnpicklingError,
            ValueError,
            EOFError,
            FileNotFoundError,
            TypeError,
            Exception,
        ) as e:
            raise Exception(f"Could not open {self._filename}: {e}")

        # Fill the dataframe
        for name in npy_array.dtype.names:
            if name == "dcr":
                # In version 2, the dcr is 2D: dcr[:, 0] corresponds to the dcr of
                # version 1, while dcr[:, 1] is just 1.0 - dcr[:, 0]. We drop the
                # second dimension.
                df["dcr"] = npy_array["dcr"][:, 0]
                continue

            # Special cases
            if name == "loc":
                df["x"] = npy_array["loc"][:, 0]
                df["y"] = npy_array["loc"][:, 1]
                df["z"] = npy_array["loc"][:, 2]
                continue

            if name == "lnc":
                df["lncx"] = npy_array["lnc"][:, 0]
                df["lncy"] = npy_array["lnc"][:, 1]
                df["lncz"] = npy_array["lnc"][:, 2]
                continue

            # Single arrays
            df[name] = npy_array[name]

        return df

    def _load_mat(self, df: pd.DataFrame):
        """Load the MAT file and update the dataframe."""
        # Load .mat file
        try:
            mat_array = loadmat(str(self._filename))
        except (FileNotFoundError, ValueError) as e:
            raise Exception(f"Could not open {self._filename}: {e}")

        # Fill the dataframe
        for key in mat_array.keys():
            if key in ["__header__", "__version__", "__globals__"]:
                continue

            if key == "dcr":
                # In version 2, the dcr is 2D: dcr[:, 0] corresponds to the dcr of
                # version 1, while dcr[:, 1] is just 1.0 - dcr[:, 0]. We drop the
                # second dimension.
                df["dcr"] = mat_array["dcr"][:, 0]
                continue

            # Special cases
            if key == "loc":
                df["x"] = mat_array["loc"][:, 0]
                df["y"] = mat_array["loc"][:, 1]
                df["z"] = mat_array["loc"][:, 2]
                continue

            if key == "lnc":
                df["lncx"] = mat_array["lnc"][:, 0]
                df["lncy"] = mat_array["lnc"][:, 1]
                df["lncz"] = mat_array["lnc"][:, 2]
                continue

            # Single arrays
            df[key] = mat_array[key].ravel()

        return df

    def _load_json(self, df: pd.DataFrame):
        """Load the JSON file and update the dataframe."""

        # Load array
        try:
            with open(str(self._filename), "r", encoding="utf-8") as f:
                json_array = json.load(f)
        except (
            FileNotFoundError,
            UnicodeDecodeError,
            JSONDecodeError,
            Exception,
        ) as e:
            raise Exception(f"Could not open {self._filename}: {e}")

        # Create a dictionary of empty lists and keys matching the loaded ones
        dict_keys = list(json_array[0].keys()) + ["x", "y", "z", "lncx", "lncy", "lncz"]
        d = {key: [] for key in dict_keys}
        del d["loc"]
        del d["lnc"]
        for entry in json_array:
            for key in entry:
                if key == "dcr":
                    # In version 2, the dcr is 2D: dcr[:, 0] corresponds to the dcr of
                    # version 1, while dcr[:, 1] is just 1.0 - dcr[:, 0]. We drop the
                    # second dimension.
                    d["dcr"].append(entry["dcr"][0])
                    continue

                    # Special cases
                if key == "loc":
                    d["x"].append(entry["loc"][0])
                    d["y"].append(entry["loc"][1])
                    d["z"].append(entry["loc"][2])
                    continue

                if key == "lnc":
                    d["lncx"].append(entry["lnc"][0])
                    d["lncy"].append(entry["lnc"][1])
                    d["lncz"].append(entry["lnc"][2])
                    continue

                d[key].append(entry[key])

        # Fill dataframe
        for key in d:
            df[key] = d[key]

        return df

    def _load_pmx(self, df: pd.DataFrame):
        """Load the PMX file and update the dataframe."""
        # Read filtered dataframe
        df = PMXReader.get_dataframe(self._filename)

        return df

    def _set_all_indices(self):
        """Set indices of properties to be read."""
        if self.num_valid_entries == 0:
            return False

        # Number of iterations
        self._reps = int(np.max(self._full_raw_dataframe["itr"]) + 1)

        # Is this an aggregated acquisition?
        self._is_aggregated = self._reps == 1

        # Query the data to find the last valid iteration
        # for all measurements
        try:
            last_valid = find_last_valid_iteration_v2(
                self._full_raw_dataframe, num_iterations=self._reps
            )
        except ValueError as e:
            print(f"[ERROR] {e}")
            return False

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

        # Inform
        # @TODO Remove after testing
        print(
            f"[DEBUG] "
            f"efo: {self._efo_index},"
            f"cfr: {self._cfr_index}, "
            f"dcr: {self._dcr_index}, "
            f"eco: {self._eco_index}, "
            f"loc: {self._loc_index}, "
            f"valid_cfr: {self._valid_cfr}, "
            f"reloc: {self._relocalizations}, "
            f"last_valid: {self._last_valid}, "
            f"last_valid_cfr: {self._last_valid_cfr}"
        )

    def _extend_array_with_prepend(self, arr: np.array, n: int):
        """
        Extends the input sorted NumPy array by prepending `n` consecutive values before each element.
        Elements where the gap from the previous kept element is <= `n` are discarded.

        Parameters
        ----------

        arr: np.ndarray
            Sorted 1D NumPy array of integers.

        n: int
            Number of consecutive values to prepend before each element.

        Returns
        -------

        ext_arr: np.ndarray
            Extended array with new values prepended.
        """

        # Compute differences between consecutive elements
        diffs = np.diff(arr)

        # The first element is always kept
        keep_mask = np.concatenate(([True], diffs > n))

        # Select elements to keep
        kept_elements = arr[keep_mask]

        # Generate new values for each kept element
        # For each element x in kept_elements, generate x-n, x-(n-1), ..., x-1
        prepend_offsets = np.arange(n, 0, -1)
        new_values = (
            kept_elements[:, np.newaxis] - prepend_offsets
        )  # Shape: (num_kept, n)

        # Flatten the new_values array
        new_values = new_values.flatten()

        # Combine new values with the kept elements
        combined = np.concatenate((new_values, kept_elements))

        # Remove any potential duplicates and ensure the array is sorted
        extended_array = np.unique(combined)

        return extended_array

    def _get_valid_subset(self):
        """Returns the valid subset of the full dataframe from which to
        extract the requested iteration data."""

        if self._valid:
            val_indices = self._valid_entries
        else:
            val_indices = np.logical_not(self._valid_entries)

        # Valid
        data_valid_df = self._full_raw_dataframe[val_indices]

        # Here we have to use different logic for tracking vs. localization
        # acquisitions. Tracking (and potentially other custom sequences)
        # only have one cfr value per trace id.
        condition = (data_valid_df["itr"].eq(self._cfr_index)).groupby(
            data_valid_df["tid"]
        ).sum() == 1
        one_cfr_per_tid = np.all(condition)

        if one_cfr_per_tid:
            # Traces that only have one cfr in the first localization (and then not
            # measured anymore) are a special case of incomplete iterations. In this
            # case, we do not want to drop them: to make them valid, we copy the cfr
            # value from the first iterations to all subsequent localizations.
            indices = data_valid_df.index[
                (data_valid_df["itr"] == self._cfr_index)
                | (data_valid_df["itr"] == self._loc_index)
            ].to_numpy()
        else:
            # For localizations, we preserve only all those iterations that have a full set
            # from the cfr iteration to the localized iteration: but for those we make sure
            # to have all relocalizations to support dcr pooling
            indices = data_valid_df.index[
                data_valid_df["itr"] == self._loc_index
            ].to_numpy()
            if self._pool_dcr:
                start_index = (
                    self._loc_index
                    - np.sum(self.relocalizations[: self._loc_index + 1])
                    + 1
                )
            else:
                start_index = self._cfr_index
            num_rows = self._loc_index - start_index
            if num_rows > 0:
                indices = self._extend_array_with_prepend(indices, num_rows)

            # @TODO DEBUG: remove when properly tested
            # assert np.all(np.unique(data_valid_df.iloc[indices]["itr"]) == np.arange(self._cfr_index, self._loc_index + 1))

        return indices

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

        # Get valid subset
        valid_subset = self._get_valid_subset()
        data_valid_df = self._full_raw_dataframe.loc[valid_subset]

        # Extract the iteration IDs
        iid = data_valid_df["iid"].to_numpy()

        # Extract the valid iterations
        itr = data_valid_df["itr"].to_numpy()

        # Extract the valid identifiers
        tid = data_valid_df["tid"].to_numpy()

        # Extract the valid time points
        tim = data_valid_df["tim"].to_numpy()

        # Extract the fluorophore IDs
        fluo = data_valid_df["fluo"].to_numpy()
        if np.all(fluo) == 0:
            fluo = np.ones(fluo.shape, dtype=fluo.dtype)

        # The following extraction pattern will change whether the
        # acquisition is normal or aggregated
        if self.is_aggregated:
            # Extract the locations
            x = data_valid_df["x"].to_numpy()
            y = data_valid_df["y"].to_numpy()
            z = data_valid_df["z"].to_numpy()
            z *= self._z_scaling_factor

            # Extract EFO
            efo = data_valid_df["efo"].to_numpy()

            # Extract CFR
            cfr = data_valid_df["cfr"].to_numpy()

            # Extract ECO
            eco = data_valid_df["eco"].to_numpy()

            # Extract DCR
            dcr = data_valid_df["dcr"].to_numpy()

            # Extract the background
            fbg = data_valid_df["fbg"].to_numpy()

            # Dwell
            dwell = np.around((eco / (efo / 1000)) / self._dwell_time, decimals=0)

        else:
            # In contrast to version 1 of the reader and of the Imspector file formats, we now extract
            # by value and not by index!

            # Extract the iteration IDs
            iid = iid[itr == self._loc_index]

            # Trace IDs
            tid = tid[itr == self._loc_index]

            # Extract the valid time points
            tim = tim[itr == self._loc_index]

            # Extract the locations
            loc = (
                data_valid_df[["x", "y", "z"]][itr == self._loc_index]
                * self._unit_scaling_factor
            )
            loc["z"] *= self._z_scaling_factor
            x = loc["x"].to_numpy()
            y = loc["y"].to_numpy()
            z = loc["z"].to_numpy()

            # Extract EFO
            efo = data_valid_df["efo"][itr == self._efo_index].to_numpy()

            # Extract CFR (conditional to the presence of the last loc)
            cfr = data_valid_df["cfr"][itr == self._cfr_index].to_numpy()
            if len(cfr) < len(tid):
                # This is the (tracking) case where the cfr value is
                # stored from a non-relocalized iteration. Moreover,
                # this cfr is only measured for the first, complete,
                # sequence of the trace.
                _, counts = np.unique(tid, return_counts=True)
                cfr = np.repeat(cfr, counts)

            # Extract ECO
            eco = data_valid_df["eco"][itr == self._eco_index].to_numpy()

            # Extract the background
            fbg = data_valid_df["fbg"][itr == self._loc_index].to_numpy()

            # Fluorophore
            fluo = data_valid_df["fluo"][itr == self._loc_index].to_numpy()

            # Pool DCR values?
            num_relocs = int(np.sum(self._relocalizations[: self._loc_index + 1]))
            if self._pool_dcr and num_relocs > 1:

                # Calculate ECO contributions
                eco_all = data_valid_df["eco"].to_numpy().reshape(-1, num_relocs)
                eco_sum = eco_all.sum(axis=1)
                eco_all_norm = eco_all / eco_sum.reshape(-1, 1)

                # Extract DCR values and weigh them by the relative ECO contributions
                dcr = data_valid_df["dcr"].to_numpy().reshape(-1, num_relocs)
                dcr = dcr * eco_all_norm
                dcr = dcr.sum(axis=1)

            else:

                # Extract DCR
                dcr = data_valid_df["dcr"][itr == self._dcr_index].to_numpy()

            # Calculate dwell
            dwell = np.around((eco / (efo / 1000)) / self._dwell_time, decimals=0)

        # Create a Pandas dataframe for the results (make sure to use properties
        # from the V2 reader
        df = pd.DataFrame(
            index=pd.RangeIndex(start=0, stop=len(tid)),
            columns=self.processed_properties(),
        )

        # Store the extracted valid hits into the dataframe
        df["tid"] = tid
        df["x"] = x
        df["y"] = y
        df["z"] = z
        df["tim"] = tim
        df["efo"] = efo
        df["cfr"] = cfr
        df["eco"] = eco
        df["dcr"] = dcr
        df["dwell"] = dwell
        df["fbg"] = fbg
        df["fluo"] = fluo
        df["iid"] = iid

        # Check if the selected indices correspond to the last valid iteration
        self._is_last_valid = bool(
            self._cfr_index == self._last_valid_cfr
            and self._efo_index == self._last_valid
        )

        return df
