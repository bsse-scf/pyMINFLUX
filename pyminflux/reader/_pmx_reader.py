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
from typing import Union

import h5py
import pandas as pd

from pyminflux.reader.metadata import PMXMetadata
from pyminflux.reader.util import version_str_to_int


class PMXReader:
    """Reader of (processed) MINFLUX from native `.pmx` format."""

    @staticmethod
    def get_metadata(filename) -> Union[PMXMetadata, None]:
        """Reads metadata information from `.pmx` files."""

        # Open the file
        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            # First, check that the version is known
            if file_version not in ["1.0", "2.0", "3.0"]:
                return None

            # Convert version string to number
            version_int = version_str_to_int(file_version)

            # Initialize parameters (for versions above version 1.0)
            tr_len_thresholds = None
            time_thresholds = None
            dwell_time = 1.0
            is_tracking = False
            pool_dcr = False
            scale_bar_size = 500

            # Version 1.0 parameters
            if version_int > 0:

                try:
                    z_scaling_factor = float(f["parameters/z_scaling_factor"][()])
                except KeyError:
                    return None

                try:
                    min_trace_length = int(f["parameters/min_trace_length"][()])
                except KeyError:
                    return None

                try:
                    efo_thresholds = tuple(f["parameters/applied_efo_thresholds"][:])
                except KeyError as e:
                    efo_thresholds = None
                try:
                    cfr_thresholds = tuple(f["parameters/applied_cfr_thresholds"][:])
                except KeyError as e:
                    cfr_thresholds = None

                try:
                    num_fluorophores = int(f["parameters/num_fluorophores"][()])
                except KeyError:
                    return None

            # Version 2.0 parameters
            if version_int > 10000:
                # Parameters are present in the file, and we can read them

                try:
                    # This setting can be missing
                    tr_len_thresholds = tuple(
                        f["parameters/applied_tr_len_thresholds"][:]
                    )
                except KeyError as e:
                    tr_len_thresholds = None

                try:
                    dwell_time = float(f["parameters/dwell_time"][()])
                except KeyError as e:
                    return None

                try:
                    # This setting can be missing
                    time_thresholds = tuple(f["parameters/applied_time_thresholds"][:])
                except KeyError as e:
                    time_thresholds = None

                # HDF5 does not have a native boolean type, so we save as int8 and convert it
                # back to boolean on read.
                try:
                    is_tracking = bool(f["parameters/is_tracking"][()])
                except KeyError as e:
                    return None

                try:
                    pool_dcr = bool(f["parameters/pool_dcr"][()])
                except KeyError as e:
                    # This is an addendum to version 2.0, and we allow it to be missing.
                    # It will fall back to False.
                    pool_dcr = False

                try:
                    scale_bar_size = float(f["parameters/scale_bar_size"][()])
                except KeyError as e:
                    return None

            # Version 3.0 parameters
            # No new parameters

        # Store and return
        metadata = PMXMetadata(
            pool_dcr=pool_dcr,
            cfr_thresholds=cfr_thresholds,
            dwell_time=dwell_time,
            efo_thresholds=efo_thresholds,
            is_tracking=is_tracking,
            min_trace_length=min_trace_length,
            num_fluorophores=num_fluorophores,
            scale_bar_size=scale_bar_size,
            time_thresholds=time_thresholds,
            tr_len_thresholds=tr_len_thresholds,
            z_scaling_factor=z_scaling_factor,
        )

        return metadata

    @staticmethod
    def get_dataframe(filename: Union[Path, str]):
        """Return the full dataframe.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version != "3.0":
                return None

            # Read the reader_version attribute: it must be 2
            reader_version = f.attrs["reader_version"]
            if reader_version != 2:
                raise ValueError("`reader_version` must be 2.")

            #
            # Read raw dataset
            #
            dataset = f["/raw/df"]

            # Read the NumPy data
            data_array = dataset[:]

            # Read column names
            column_names = dataset.attrs["column_names"]

            # Read column data types
            column_types = dataset.attrs["column_types"]

            # Read the index
            index_data = f["/raw/df_index"][:]

            # Create DataFrame with specified columns
            df = pd.DataFrame(data_array, index=index_data, columns=column_names)

            # Apply column data types
            for col, dtype in zip(column_names, column_types):
                df[col] = df[col].astype(dtype)

            return df

    @staticmethod
    def get_filtered_dataframe(filename: Union[Path, str]):
        """Reads the Pandas DataFrame from `.pmx` files versions 1.0, 2.0, and 3.0.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version not in ["1.0", "2.0", "3.0"]:
                return None

            # Read dataset
            dataset = f["/paraview/dataframe"]

            # Read the NumPy data
            data_array = dataset[:]

            # Read column names
            column_names = dataset.attrs["column_names"]

            # Read column data types
            column_types = dataset.attrs["column_types"]

            # Read the index
            index_data = f["/paraview/dataframe_index"][:]

            # Create DataFrame with specified columns
            df = pd.DataFrame(data_array, index=index_data, columns=column_names)

            # Apply column data types
            for col, dtype in zip(column_names, column_types):
                df[col] = df[col].astype(dtype)

        return df

    @staticmethod
    def get_array(filename: Union[Path, str]):
        """Returns the raw Numpy array (filtered). This applies to:

        - pmx files version 1.0, 2.0
        - pmx files version 3.0 with reader version 1

        pmx files version 3.0 with reader version 2 only store the (filtered) raw dataframe.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        # Open the file and read the data
        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version not in ["1.0", "2.0", "3.0"]:
                return None

            if file_version == "3.0":
                reader_version = f.attrs["reader_version"]
                if reader_version == 1:
                    data_array = f["raw/npy"][:]
                else:
                    return None
            else:
                # We only read the raw NumPy array
                data_array = f["raw/npy"][:]

        return data_array
