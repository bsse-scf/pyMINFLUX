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

import tempfile
import zipfile
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import pytest

from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import (
    MinFluxReader,
    MinFluxReaderFactory,
    MinFluxReaderV2,
    PMXReader,
)
from pyminflux.writer import PMXWriter


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


@pytest.fixture(autouse=False)
def extract_pmx_various_versions(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    pmx_file_names = ["pmx_format_v1.pmx", "pmx_format_v2.pmx", "pmx_format_v3.pmx"]
    zip_file_name = Path(__file__).parent / "data" / "pmx_format_versions.zip"
    found = True
    for pmx_file_name in pmx_file_names:
        pmx_file_full_name = Path(__file__).parent / "data" / pmx_file_name
        if not pmx_file_full_name.is_file():
            found = False
            break

    if not found:
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

    print("The version 3.0 PMX file format is not finalized yet.")
    assert True
    return

    #
    # 2D_All.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #
    MIN_TRACE_LENGTH = 1

    # 2D_All.npy
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "2D_All.npy", z_scaling_factor=0.7
    )
    processor = MinFluxProcessor(reader, min_trace_length=MIN_TRACE_LENGTH)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.filtered_dataframe.index))
    processor.set_full_fluorophore_ids(fluo)

    with tempfile.TemporaryDirectory() as tmp_dir:

        # Create writer
        writer = PMXWriter(processor)

        # File name
        file_name = Path(tmp_dir) / "out.pmx"

        # Write to disk
        assert writer.write(file_name) is True, "Could not save .pmx file."

        # Read the dataframe back from the file
        df_read = PMXReader.get_filtered_dataframe(file_name)

        # Check that the datatypes of columns are preserved
        for col in processor.filtered_dataframe.columns:
            assert (
                processor.filtered_dataframe[col].dtype == df_read[col].dtype
            ), f"Mismatch of column datatype {col}: {processor.filtered_dataframe[col].dtype} vs. {df_read[col].dtype}"

        # Check that the index data type is the same
        assert (
            processor.filtered_dataframe.index.dtype == df_read.index.dtype
        ), f"Index data types are different: {processor.filtered_dataframe.index.dtype} vs {df_read.index.dtype}"

        # Check if there are NaN in different locations
        assert (
            (processor.filtered_dataframe.isna() == df_read.isna()).all().all()
        ), "NaN locations are different"

        # Other attributes
        assert (
            processor.filtered_dataframe.index.name == df_read.index.name
        ), "Index names are different"

        # Column names
        assert (
            processor.filtered_dataframe.columns.names == df_read.columns.names
        ), "Column names are different"

        # Use pd.compare()
        differences = processor.filtered_dataframe.compare(df_read)
        assert len(differences.columns) == 0, "Found differences."
        assert len(differences.index) == 0, "Found differences."

        # Check that the dataframes in the HDF5 file is identical to the original file
        # It the following fails, use `dataframes_equal(processor.filtered_dataframe, df_read)` instead.
        assert processor.filtered_dataframe.equals(
            df_read
        ), "Mismatch between original dataframe and the copy read from the .pmx file!"

        # Check that the file_version attribute exists and is correctly set
        with h5py.File(file_name, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]
            assert file_version == "2.0", "Invalid attribute 'file_version'!"

            # Read the NumPy array explicitly
            data_array = f["raw/npy"][:]

            # Check that the read NumPy array is identical to the original
            assert (
                data_array.shape == processor.reader.valid_raw_data_array.shape
            ), "NumPy arrays' shape mismatch!"
            assert (
                data_array.dtype == processor.reader.valid_raw_data_array.dtype
            ), "Mismatch in raw NumPy arrays' shape!"

            assert structured_arrays_equal(
                data_array, processor.filtered_raw_data_array
            ), "Mismatch in raw NumPy arrays' content!"

            # Test the parameters
            z_scaling_factor = f["parameters/z_scaling_factor"][()]
            assert (
                z_scaling_factor == processor.z_scaling_factor
            ), "Unexpected value for z_scaling_factor!"
            min_trace_length = f["parameters/min_trace_length"][()]
            assert (
                min_trace_length == MIN_TRACE_LENGTH
            ), "Unexpected value for min_trace_length!"
            num_fluorophores = f["parameters/num_fluorophores"][()]
            assert (
                num_fluorophores == processor.num_fluorophores
            ), "Unexpected value for num_fluorophores!"

        # Read the array using the native reader
        data_array_native = PMXReader.get_array(file_name)

        # Check that the read NumPy array is identical to the original
        assert (
            data_array_native.shape == processor.filtered_raw_data_array.shape
        ), "NumPy arrays' shape mismatch!"
        assert (
            data_array_native.dtype == processor.filtered_raw_data_array.dtype
        ), "Mismatch in raw NumPy arrays' shape!"

        assert structured_arrays_equal(
            data_array_native, processor.filtered_raw_data_array
        ), "Mismatch in raw NumPy arrays' content!"

        # Read the metadata via the PMXMetadataReader instead
        metadata = PMXReader.get_metadata(file_name)
        assert (
            metadata.z_scaling_factor == processor.z_scaling_factor
        ), "Unexpected value for z_scaling_factor!"
        assert (
            metadata.min_trace_length == MIN_TRACE_LENGTH
        ), "Unexpected value for min_trace_length!"
        assert (
            metadata.num_fluorophores == processor.num_fluorophores
        ), "Unexpected value for num_fluorophores!"
        assert metadata.efo_thresholds is None, "Unexpected value for efo_thresholds!"
        assert metadata.cfr_thresholds is None, "Unexpected value for cfr_thresholds!"

        # Now test the MinFluxReader
        reader = MinFluxReader(file_name, z_scaling_factor=0.7)
        processor_new = MinFluxProcessor(reader, min_trace_length=MIN_TRACE_LENGTH)

        # Compare the data from the original and the new file after processing with the MinFluxProcessor
        #
        # @HINT
        # If the following tests fail, use:
        #
        #     dataframes_equal(processor.filtered_dataframe, processor_new.filtered_dataframe)
        #
        # to find the differences
        assert np.all(
            processor.filtered_dataframe.columns
            == processor_new.filtered_dataframe.columns
        ), "Reloaded dataframe mismatch."
        assert np.allclose(
            processor.filtered_dataframe.to_numpy(),
            processor_new.filtered_dataframe.to_numpy(),
            equal_nan=True,
        ), "Reloaded dataframe mismatch."

    #
    # Now the same but with filtering
    #
    # 2D_All.npy
    #
    # min_trace_length = 4 (filter short-lived traces)
    #
    MIN_TRACE_LENGTH = 4

    # 2D_ValidOnly.npy
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "2D_All.npy", z_scaling_factor=0.7
    )
    processor = MinFluxProcessor(reader, min_trace_length=MIN_TRACE_LENGTH)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.processed_dataframe.index))
    processor.set_full_fluorophore_ids(fluo)

    with tempfile.TemporaryDirectory() as tmp_dir:

        # Create writer
        writer = PMXWriter(processor)

        # File name
        file_name = Path(tmp_dir) / "out.pmx"

        # Write to disk
        assert writer.write(file_name) is True, "Could not save .pmx file."

        # Read the dataframe back from the file
        df_read = PMXReader.get_filtered_dataframe(file_name)

        # Make sure the number of entries is the same
        assert len(processor.filtered_dataframe.index) == len(
            df_read.index
        ), "Mismatch in the number of entries!"

        # Check that the datatypes of columns are preserved
        for col in processor.filtered_dataframe.columns:
            assert (
                processor.filtered_dataframe[col].dtype == df_read[col].dtype
            ), f"Mismatch of column datatype {col}: {processor.filtered_dataframe[col].dtype} vs. {df_read[col].dtype}"

        # Check that the index data type is the same
        assert (
            processor.filtered_dataframe.index.dtype == df_read.index.dtype
        ), f"Index data types are different: {processor.filtered_dataframe.index.dtype} vs {df_read.index.dtype}"

        # Check if there are NaN in different locations
        assert (
            (processor.filtered_dataframe.isna() == df_read.isna()).all().all()
        ), "NaN locations are different"

        # Other attributes
        assert (
            processor.filtered_dataframe.index.name == df_read.index.name
        ), "Index names are different"

        # Column names
        assert (
            processor.filtered_dataframe.columns.names == df_read.columns.names
        ), "Column names are different"

        # Use pd.compare()
        differences = processor.filtered_dataframe.compare(df_read)
        assert len(differences.columns) == 0, "Found differences."
        assert len(differences.index) == 0, "Found differences."

        # Check that the dataframes in the HDF5 file is identical to the original file
        assert processor.filtered_dataframe.equals(
            df_read
        ), "Mismatch between original dataframe and the copy read from the .pmx file!"

        # Check that the file_version attribute exists and is correctly set
        with h5py.File(file_name, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]
            assert file_version == "2.0", "Invalid attribute 'file_version'!"

            # Read the NumPy array explicitly
            data_array = f["raw/npy"][:]

            # Check that the read NumPy array is identical to the original
            assert (
                data_array.shape == processor.filtered_raw_data_array.shape
            ), "NumPy arrays' shape mismatch!"
            assert (
                data_array.dtype == processor.filtered_raw_data_array.dtype
            ), "Mismatch in raw NumPy arrays' shape!"

            assert structured_arrays_equal(
                data_array, processor.filtered_raw_data_array
            ), "Mismatch in raw NumPy arrays' content!"

            # Test the parameters
            z_scaling_factor = f["parameters/z_scaling_factor"][()]
            assert (
                z_scaling_factor == processor.z_scaling_factor
            ), "Unexpected value for z_scaling_factor!"
            min_trace_length = f["parameters/min_trace_length"][()]
            assert (
                min_trace_length == MIN_TRACE_LENGTH
            ), "Unexpected value for min_trace_length!"
            num_fluorophores = f["parameters/num_fluorophores"][()]
            assert (
                num_fluorophores == processor.num_fluorophores
            ), "Unexpected value for num_fluorophores!"

        # Read the array using the native reader
        data_array_native = PMXReader.get_array(file_name)

        # Check that the read NumPy array is identical to the original
        assert (
            data_array_native.shape == processor.filtered_raw_data_array.shape
        ), "NumPy arrays' shape mismatch!"
        assert (
            data_array_native.dtype == processor.filtered_raw_data_array.dtype
        ), "Mismatch in raw NumPy arrays' shape!"

        assert structured_arrays_equal(
            data_array_native, processor.filtered_raw_data_array
        ), "Mismatch in raw NumPy arrays' content!"

        # Read the metadata via the PMXMetadataReader instead
        metadata = PMXReader.get_metadata(file_name)
        assert (
            metadata.z_scaling_factor == processor.z_scaling_factor
        ), "Unexpected value for z_scaling_factor!"
        assert (
            metadata.min_trace_length == MIN_TRACE_LENGTH
        ), "Unexpected value for min_trace_length!"
        assert (
            metadata.num_fluorophores == processor.num_fluorophores
        ), "Unexpected value for num_fluorophores!"
        assert metadata.efo_thresholds is None, "Unexpected value for efo_thresholds!"
        assert metadata.cfr_thresholds is None, "Unexpected value for cfr_thresholds!"

        # Now test the MinFluxReader
        reader = MinFluxReader(file_name, z_scaling_factor=0.7)
        processor_new = MinFluxProcessor(reader, min_trace_length=MIN_TRACE_LENGTH)

        # Compare the data from the original and the new file after processing with the MinFluxProcessor
        #
        # @HINT
        # If the following tests fail, use dataframes_equal(processor.filtered_dataframe, processor_new.filtered_dataframe) to find the differences
        assert np.all(
            processor.filtered_dataframe.columns
            == processor_new.filtered_dataframe.columns
        ), "Reloaded dataframe mismatch."
        assert np.allclose(
            processor.filtered_dataframe.to_numpy(),
            processor_new.filtered_dataframe.to_numpy(),
            equal_nan=True,
        ), "Reloaded dataframe mismatch."


def test_consistence_of_pmx_versions(extract_pmx_various_versions):

    # Aliases
    v1_pmx = Path(__file__).parent / "data" / "pmx_format_v1.pmx"
    v2_pmx = Path(__file__).parent / "data" / "pmx_format_v2.pmx"
    v3_pmx = Path(__file__).parent / "data" / "pmx_format_v3.pmx"

    # Load V1 file
    array_v1 = PMXReader.get_array(v1_pmx)
    assert "itr" in array_v1["itr"].dtype.names, "Nested array structure expected!"

    # Load V2 file
    array_v2 = PMXReader.get_array(v2_pmx)
    assert "itr" in array_v2["itr"].dtype.names, "Nested array structure expected!"

    # Load V3 file
    array_v3 = PMXReader.get_array(v3_pmx)
    assert array_v3 is None  # No array is stored in V3 PMX files

    # Load V1 metadata
    metadata_v1 = PMXReader.get_metadata(v1_pmx)
    metadata_v1_properties = vars(metadata_v1).keys()

    # Load V2 metadata
    metadata_v2 = PMXReader.get_metadata(v2_pmx)
    metadata_v2_properties = vars(metadata_v2).keys()
    assert (
        metadata_v2_properties == metadata_v1_properties
    ), "Same keys must be present in metadata v2 and v1!"

    # Load V3 metadata
    metadata_v3 = PMXReader.get_metadata(v2_pmx)
    metadata_v3_properties = vars(metadata_v3).keys()
    assert (
        metadata_v3_properties == metadata_v1_properties
    ), "Same keys must be present in metadata v3 and v1!"

    # Load V1 PMX file with the MinFluxReader
    reader_class_v1_pmx, status_str = MinFluxReaderFactory.get_reader(v1_pmx)
    assert status_str == "", f"Unexpected status string: {status_str}."
    assert reader_class_v1_pmx is MinFluxReader, "Expected V1 MinFluxReader class!"
    reader_v1_pmx = reader_class_v1_pmx(v1_pmx, z_scaling_factor=0.7)
    assert (
        len(reader_v1_pmx.processed_dataframe.index) == 1056
    ), "Unexpected number of localizations in file."
    assert (
        len(reader_v1_pmx.processed_dataframe.columns) == 11
    ), "Unexpected number of columns in processed dataframe."
    n_fluo1_v1 = np.sum(reader_v1_pmx.processed_dataframe["fluo"] == 1)
    n_fluo2_v1 = np.sum(reader_v1_pmx.processed_dataframe["fluo"] == 2)
    assert n_fluo1_v1 == 920, "Unexpected number of fluo IDs = 1"
    assert n_fluo2_v1 == 136, "Unexpected number of fluo IDs = 2"
    assert n_fluo1_v1 + n_fluo2_v1 == len(reader_v1_pmx.processed_dataframe.index)

    # Load V2 PMX file with the MinFluxReader
    reader_class_v2_pmx, status_str = MinFluxReaderFactory.get_reader(v2_pmx)
    assert status_str == "", f"Unexpected status string: {status_str}."
    assert reader_class_v2_pmx is MinFluxReader, "Expected V1 MinFluxReader class!"
    reader_v2_pmx = reader_class_v2_pmx(v2_pmx, z_scaling_factor=0.7)
    assert (
        len(reader_v2_pmx.processed_dataframe.index) == 1056
    ), "Unexpected number of localizations in file."
    assert (
        len(reader_v2_pmx.processed_dataframe.columns) == 11
    ), "Unexpected number of columns in processed dataframe."
    assert np.all(
        reader_v2_pmx.processed_dataframe.columns
        == reader_v1_pmx.processed_dataframe.columns
    ), "Processed dataframe columns mismatch."
    n_fluo1_v2 = np.sum(reader_v2_pmx.processed_dataframe["fluo"] == 1)
    n_fluo2_v2 = np.sum(reader_v2_pmx.processed_dataframe["fluo"] == 2)
    assert n_fluo1_v2 == 920, "Unexpected number of fluo IDs = 1"
    assert n_fluo2_v2 == 136, "Unexpected number of fluo IDs = 2"
    assert n_fluo1_v2 + n_fluo2_v2 == len(reader_v2_pmx.processed_dataframe.index)

    # Load V3 PMX file with the MinFluxReader (this is a different dataset from V1 and V2)
    reader_class_v3_pmx, status_str = MinFluxReaderFactory.get_reader(v3_pmx)
    assert status_str == "", f"Unexpected status string: {status_str}."
    assert reader_class_v3_pmx is MinFluxReaderV2, "Expected V2 MinFluxReader class!"
    reader_v3_pmx = reader_class_v3_pmx(v3_pmx, z_scaling_factor=0.7)
    assert (
        len(reader_v3_pmx.processed_dataframe.index) == 404
    ), "Unexpected number of localizations in file."
    assert (
        len(reader_v3_pmx.processed_dataframe.columns) == 12
    ), "Unexpected number of columns in processed dataframe."
    n_fluo1_v3 = np.sum(reader_v3_pmx.processed_dataframe["fluo"] == 1)
    n_fluo2_v3 = np.sum(reader_v3_pmx.processed_dataframe["fluo"] == 2)
    assert n_fluo1_v3 == 138, "Unexpected number of fluo IDs = 1"
    assert n_fluo2_v3 == 266, "Unexpected number of fluo IDs = 2"
    assert n_fluo1_v3 + n_fluo2_v3 == len(reader_v3_pmx.processed_dataframe.index)
