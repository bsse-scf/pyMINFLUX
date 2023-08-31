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
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import h5py
import pandas as pd


@dataclass
class Metadata:
    z_scaling_factor: float
    min_trace_length: int
    efo_thresholds: tuple[int, int]
    cfr_thresholds: tuple[float, float]
    num_fluorophores: int


class NativeMetadataReader:
    """Reads metadata information from `.pmx` files."""

    @staticmethod
    def scan(filename: Union[Path, str]):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        # Open the file
        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version != "1.0":
                return None

            # Read the parameters
            z_scaling_factor = f["parameters/z_scaling_factor"][()]
            min_trace_length = f["parameters/min_trace_length"][()]
            try:
                efo_thresholds = tuple(f["parameters/applied_efo_thresholds"][:])
            except KeyError as e:
                efo_thresholds = None
            try:
                cfr_thresholds = tuple(f["parameters/applied_cfr_thresholds"][:])
            except KeyError as e:
                cfr_thresholds = None
            num_fluorophores = f["parameters/num_fluorophores"][()]

        # Store and return
        metadata = Metadata(
            z_scaling_factor=z_scaling_factor,
            min_trace_length=min_trace_length,
            efo_thresholds=efo_thresholds,
            cfr_thresholds=cfr_thresholds,
            num_fluorophores=num_fluorophores,
        )

        return metadata


class NativeArrayReader:
    """Reads the native NumPy array from `.pmx` files."""

    @staticmethod
    def read(filename: Union[Path, str]):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        # Open the file and read the data
        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version != "1.0":
                return None

            # We only read the raw NumPy array
            data_array = f["raw/npy"][:]

        return data_array


class NativeDataFrameReader:
    """Reads the Pandas DataFrame from `.pmx` files."""

    @staticmethod
    def read(filename: Union[Path, str]):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version != "1.0":
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
