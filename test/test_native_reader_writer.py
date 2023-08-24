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

import tempfile
import zipfile
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import pytest

from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.writer import PyMinFluxNativeWriter


@pytest.fixture(autouse=False)
def extract_raw_npy_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    npy_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy"
    zip_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def structured_arrays_equal(arr1, arr2):
    if arr1.shape != arr2.shape or arr1.dtype != arr2.dtype:
        return False

    # Function to compare two values, considering NaNs as equal
    def values_equal(value1, value2):
        if np.isnan(value1) and np.isnan(value2):
            return True
        return value1 == value2

    # Iterate through the records
    for i in range(arr1.shape[0]):
        # Compare 'itr' subfields
        for j in range(arr1["itr"][i].shape[0]):
            record1 = arr1["itr"][i][j]
            record2 = arr2["itr"][i][j]
            for subfield in record1.dtype.names:
                value1 = record1[subfield]
                value2 = record2[subfield]
                if isinstance(value1, np.ndarray):
                    # If the subfield is an array, use np.allclose
                    if not np.allclose(value1, value2, equal_nan=True):
                        print(
                            f"Mismatch: ['itr'][{i}][{j}['{subfield}']: {value1} vs {value2}"
                        )
                        return False
                else:
                    # If the subfield is a scalar, use values_equal function
                    if not values_equal(value1, value2):
                        print(
                            f"Mismatch: ['itr'][{i}][{j}['{subfield}']: {value1} vs {value2}"
                        )
                        return False

        # Compare other fields
        for field in ["sqi", "gri", "tim", "tid", "vld", "act", "dos", "sky", "fluo"]:
            if not values_equal(arr1[field][i], arr2[field][i]):
                print(
                    f"Mismatch: ['{field}'][{i}]: {arr1[field][i]} vs {arr2[field][i]}"
                )
                return False

    return True


def dataframes_equal(df1, df2):
    if not df1.shape == df2.shape or not (df1.columns == df2.columns).all():
        print("DataFrames must have the same shape and columns")
        return False

    for col in df1.columns:
        for idx in df1.index:
            if df1.loc[idx, col] != df2.loc[idx, col]:
                # NaNs are considered different by != operator, so check for them explicitly
                if not (pd.isna(df1.loc[idx, col]) and pd.isna(df2.loc[idx, col])):
                    print(
                        f"Column = {col}: row = {idx}: values are {df1.loc[idx, col]} and {df2.loc[idx, col]}."
                    )
                    return False

    return True


def test_consistence_of_written_pmx_files(extract_raw_npy_data_files):

    #
    # 2D_All.npy
    #
    # min_num_loc_per_trace = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "2D_All.npy", z_scaling_factor=0.7
    )
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.filtered_dataframe.index))
    processor.set_fluorophore_ids(fluo)

    with tempfile.TemporaryDirectory() as tmp_dir:

        # Create writer
        writer = PyMinFluxNativeWriter(processor)

        # File name
        file_name = Path(tmp_dir) / "out.pmx"

        # Write to disk
        assert writer.write(file_name) is True, "Could not save .pmx file."

        # Read the Pandas DataFrame explicitly with h5py
        df_read = pd.read_hdf(file_name, key="/paraview/dataframe")

        # Check that the dataframes in the HDF5 file is identical to the original file
        assert processor.filtered_dataframe.equals(
            df_read
        ), "Mismatch between original dataframe and the copy read from the .pmx file!"

        # Check that the file_version attribute exists and is correctly set
        with h5py.File(file_name, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]
            assert file_version == "1.0", "Invalid attribute 'file_version'!"

            # Read the NumPy array explicitly
            data_array = f["raw/npy"][:]

            # Check that the read NumPy array is identical to the original
            assert (
                data_array.shape == processor._reader.valid_raw_data.shape
            ), "NumPy arrays' shape mismatch!"
            assert (
                data_array.dtype == processor._reader.valid_raw_data.dtype
            ), "Mismatch in raw NumPy arrays' shape!"

            assert structured_arrays_equal(
                data_array, processor.filtered_numpy_array
            ), "Mismatch in raw NumPy arrays' content!"

            # Test the parameters
            unit_scaling_factor = f["parameters/unit_scaling_factor"][()]
            assert (
                unit_scaling_factor == processor._reader._unit_scaling_factor
            ), "Unexpected value for unit_scaling_factor!"

            z_scaling_factor = f["parameters/z_scaling_factor"][()]
            assert (
                z_scaling_factor == processor._reader._z_scaling_factor
            ), "Unexpected value for z_scaling_factor!"

        # Now test the MinFluxReader
        reader = MinFluxReader(file_name, z_scaling_factor=0.7)
        processor_new = MinFluxProcessor(reader, min_trace_length=1)

        # Compare the data from the original and the new file after processing with the MinFluxProcessor
        #
        # @HINT
        # If the following tests fail, use dataframes_equal(processor.filtered_dataframe, processor_new.filtered_dataframe) to find the differences
        assert np.all(
            processor.filtered_dataframe.columns
            == processor_new.filtered_dataframe.columns
        ), "Reloaded dataframe mismatch."
        assert np.allclose(
            processor.filtered_dataframe.values,
            processor_new.filtered_dataframe.values,
            equal_nan=True,
        ), "Reloaded dataframe mismatch."

    #
    # Now the same but with filtering
    #
    # 2D_All.npy
    #
    # min_num_loc_per_trace = 4 (filter short-lived traces)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "2D_All.npy", z_scaling_factor=0.7
    )
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.full_dataframe.index))
    processor.set_fluorophore_ids(fluo)

    with tempfile.TemporaryDirectory() as tmp_dir:

        # Create writer
        writer = PyMinFluxNativeWriter(processor)

        # File name
        file_name = Path(tmp_dir) / "out.pmx"

        # Write to disk
        assert writer.write(file_name) is True, "Could not save .pmx file."

        # Read the Pandas DataFrame explicitly with h5py
        df_read = pd.read_hdf(file_name, key="/paraview/dataframe")

        # Check that the dataframes in the HDF5 file is identical to the original file
        assert processor.filtered_dataframe.equals(
            df_read
        ), "Mismatch between original dataframe and the copy read from the .pmx file!"

        # Check that the file_version attribute exists and is correctly set
        with h5py.File(file_name, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]
            assert file_version == "1.0", "Invalid attribute 'file_version'!"

            # Read the NumPy array explicitly
            data_array = f["raw/npy"][:]

            # Check that the read NumPy array is identical to the original
            assert (
                data_array.shape == processor.filtered_numpy_array.shape
            ), "NumPy arrays' shape mismatch!"
            assert (
                data_array.dtype == processor.filtered_numpy_array.dtype
            ), "Mismatch in raw NumPy arrays' shape!"

            assert structured_arrays_equal(
                data_array, processor.filtered_numpy_array
            ), "Mismatch in raw NumPy arrays' content!"

            # Test the parameters
            unit_scaling_factor = f["parameters/unit_scaling_factor"][()]
            assert (
                unit_scaling_factor == processor._reader._unit_scaling_factor
            ), "Unexpected value for unit_scaling_factor!"

            z_scaling_factor = f["parameters/z_scaling_factor"][()]
            assert (
                z_scaling_factor == processor._reader._z_scaling_factor
            ), "Unexpected value for z_scaling_factor!"

        # Now test the MinFluxReader
        reader = MinFluxReader(file_name, z_scaling_factor=0.7)
        processor_new = MinFluxProcessor(reader, min_trace_length=1)

        # Compare the data from the original and the new file after processing with the MinFluxProcessor
        #
        # @HINT
        # If the following tests fail, use dataframes_equal(processor.filtered_dataframe, processor_new.filtered_dataframe) to find the differences
        assert np.all(
            processor.filtered_dataframe.columns
            == processor_new.filtered_dataframe.columns
        ), "Reloaded dataframe mismatch."
        assert np.allclose(
            processor.filtered_dataframe.values,
            processor_new.filtered_dataframe.values,
            equal_nan=True,
        ), "Reloaded dataframe mismatch."
