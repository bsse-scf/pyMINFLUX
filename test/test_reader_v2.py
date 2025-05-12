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

import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader, MinFluxReaderFactory, MinFluxReaderV2


@pytest.fixture(autouse=False)
def extract_multi_format_geometry_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_v2"
    target_dir.mkdir(parents=True, exist_ok=True)
    files = [
        target_dir / "241107-115322_minflux.json",
        target_dir / "241107-115322_minflux.npy",
        target_dir / "241107-115322_minflux.mat",
        target_dir / "tracking.npy",
    ]
    zip_file_name = data_dir / "reader_v2.zip"

    all_found = True
    for f in files:
        if not f.is_file():
            all_found = False
            break

    if not all_found:
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(data_dir)

    # Comparison v1 vs v2
    target_dir = data_dir / "reader_comparison"
    target_dir.mkdir(parents=True, exist_ok=True)
    files = [
        target_dir / "2d" / "v1.npy",
        target_dir / "2d" / "v2.npy",
        target_dir / "3d" / "v1.npy",
        target_dir / "3d" / "v2.npy",
    ]
    zip_file_name = data_dir / "reader_comparison.zip"

    all_found = True
    for f in files:
        if not f.is_file():
            all_found = False
            break

    if not all_found:
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(data_dir)

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_read_npy_v2(extract_multi_format_geometry_data_files):
    # Working directory
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_v2"

    #
    # Open the .npy file
    #
    npy_file_name = target_dir / "241107-115322_minflux.npy"
    numpy_array = np.load(npy_file_name)
    print(numpy_array.dtype)

    # Make sure that "itr" now is an array of integers
    assert (
        numpy_array["itr"].ndim == 1 and numpy_array["itr"].dtype == np.int32
    ), "'itr' in version 2 is now an array of integers."

    # Internal structure test
    for name in numpy_array.dtype.names:
        for i in range(len(numpy_array)):
            assert np.all(numpy_array[name][i] == numpy_array[i][name])

    # Make sure there are no NaNs in the file
    for name in numpy_array.dtype.names:
        num_nan = np.sum(numpy_array[name] == np.nan)
        assert (
            num_nan == 0
        ), f"There should be no NaNs in the array (found {num_nan} in '{name}'."

    # Check that all entries are valid
    num_vld = np.sum(numpy_array["vld"] == True)
    assert num_vld == len(numpy_array), "All entries should be valid."

    #
    # Now switch to MinFluxReaderV2 for npy
    #
    npy_file_name = target_dir / "241107-115322_minflux.npy"
    npy_reader = MinFluxReaderV2(npy_file_name, z_scaling_factor=0.7)
    assert (
        npy_reader.tot_num_entries == 69988
    ), "Unexpected number of entries in NumPy file."

    #
    # Now switch to MinFluxReaderV2 for mat
    #
    mat_file_name = target_dir / "241107-115322_minflux.mat"
    mat_reader = MinFluxReaderV2(mat_file_name, z_scaling_factor=0.7)
    assert (
        mat_reader.tot_num_entries == 69988
    ), "Unexpected number of entries in MAT file."

    # Check that the MAT dataframe is the same as the NumPy one
    assert npy_reader.processed_dataframe.equals(
        mat_reader.processed_dataframe
    ), "NumPy and MAT dataframe are different."

    #
    # Now switch to MinFluxReaderV2 for json
    #
    json_file_name = target_dir / "241107-115322_minflux.json"
    json_reader = MinFluxReaderV2(json_file_name, z_scaling_factor=0.7)
    assert (
        json_reader.tot_num_entries == 69988
    ), "Unexpected number of entries in json file."

    # Check that the json dataframe is the same as the NumPy one
    assert npy_reader.processed_dataframe.equals(
        json_reader.processed_dataframe
    ), "NumPy and json dataframe are different."


def test_reader_factory(extract_multi_format_geometry_data_files):
    # Working directory
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_v2"

    #
    # .npy
    #

    # Get the reader for the NumPy array
    npy_file_name = target_dir / "241107-115322_minflux.npy"
    reader, status = MinFluxReaderFactory.get_reader(npy_file_name)

    assert reader is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    #
    # .mat
    #

    # Get the reader for the MAT array
    mat_file_name = target_dir / "241107-115322_minflux.mat"
    reader, status = MinFluxReaderFactory.get_reader(mat_file_name)

    assert reader is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    #
    # .json
    #

    # Get the reader for the MAT array
    json_file_name = target_dir / "241107-115322_minflux.json"
    reader, status = MinFluxReaderFactory.get_reader(json_file_name)

    assert reader is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."


def test_compare_readers(extract_multi_format_geometry_data_files):
    # Working directory
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_comparison"

    #
    # 2D
    #

    # Get the reader for the NumPy array
    npy_file_name = target_dir / "2d" / "v1.npy"
    reader_class, status = MinFluxReaderFactory.get_reader(npy_file_name)
    reader = reader_class(npy_file_name, z_scaling_factor=0.7)

    assert reader_class is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader_class.__name__ == "MinFluxReader"
    ), "A reader version 1 must be returned for this file."

    # Get the reader for the NumPy array
    npy_file_name_v2 = target_dir / "2d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7)

    assert reader_v2_class is not None, "A reader must be returned for this file."
    assert status_v2 == "", "No error message expected."
    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Compare the processed dataframes
    processor = MinFluxProcessor(reader, min_trace_length=4)
    processor_v2 = MinFluxProcessor(reader_v2, min_trace_length=4)

    assert (
        processor.filtered_dataframe.columns.tolist()
        == MinFluxReader.processed_properties()
    ), "Columns mismatch."
    assert (
        processor_v2.filtered_dataframe.columns.tolist()
        == MinFluxReaderV2.processed_properties()
    ), "Columns mismatch."

    assert len(processor.filtered_dataframe.index) == len(
        processor_v2.filtered_dataframe.index
    ), "Different number of entries."
    for c in processor.filtered_dataframe:
        # Correct for the different precision of columns in v1 vs. v2
        c_v2 = processor_v2.filtered_dataframe[c].to_numpy()
        c = processor.filtered_dataframe[c].to_numpy().astype(c_v2.dtype)
        assert np.all(c == c_v2), f"Column '{c}' mismatch."

    #
    # 3D
    #

    # Get the reader for the NumPy array
    npy_file_name = target_dir / "3d" / "v1.npy"
    reader_class, status = MinFluxReaderFactory.get_reader(npy_file_name)
    reader = reader_class(npy_file_name, z_scaling_factor=0.7)

    assert reader_class is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader_class.__name__ == "MinFluxReader"
    ), "A reader version 1 must be returned for this file."

    # Get the reader for the NumPy array
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7)

    assert reader_v2 is not None, "A reader must be returned for this file."
    assert status_v2 == "", "No error message expected."
    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Compare the processed dataframes
    processor = MinFluxProcessor(reader, min_trace_length=4)
    processor_v2 = MinFluxProcessor(reader_v2, min_trace_length=4)

    assert (
        processor.filtered_dataframe.columns.tolist()
        == MinFluxReader.processed_properties()
    ), "Columns mismatch."
    assert (
        processor_v2.filtered_dataframe.columns.tolist()
        == MinFluxReaderV2.processed_properties()
    ), "Columns mismatch."

    assert len(processor.filtered_dataframe.index) == len(
        processor_v2.filtered_dataframe.index
    ), "Different number of entries."
    for c in processor.filtered_dataframe:
        # Correct for the different precision of columns in v1 vs. v2
        c_v2 = processor_v2.filtered_dataframe[c].to_numpy()
        c = processor.filtered_dataframe[c].to_numpy().astype(c_v2.dtype)
        assert np.all(c == c_v2), f"Column '{c}' mismatch."


def test_tracking_v2(extract_multi_format_geometry_data_files):
    # Working directory
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_v2"

    # Get the reader for the NumPy array
    npy_file_name_v2 = target_dir / "tracking.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7)

    assert reader_v2_class is not None, "A reader must be returned for this file."
    assert status_v2 == "", "No error message expected."
    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Explicitly set the tracking flag
    reader_v2.set_tracking(True)
    assert (
        len(reader_v2.processed_dataframe.index) == 2669
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 51
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 154
    ), "Unexpected number of unique tid values."

    # Now treat it as a localisation dataset: it still must be recognized
    # as a tracking dataset, with only one cfr per trace at the first localisation.
    del reader_v2
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7)
    reader_v2.set_tracking(False)
    assert (
        len(reader_v2.processed_dataframe.index) == 2669
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 51
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 154
    ), "Unexpected number of unique tid values."


def test_dcr_pool_v2(extract_multi_format_geometry_data_files):
    # Working directory
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_comparison"

    #
    # 2D
    #

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "2d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    assert (
        len(reader_v2.processed_dataframe.index) == 188676
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 4054
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 15755
    ), "Unexpected number of unique tid values."

    #
    # 3D
    #

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    assert (
        len(reader_v2.processed_dataframe.index) == 12709
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2047
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."


def test_non_last_valid(extract_multi_format_geometry_data_files):

    # Working directory
    data_dir = Path(__file__).parent / "data"
    target_dir = data_dir / "reader_comparison"

    #
    # 3D
    #

    # Loc index = 8

    # Get the reader for the NumPy array (with dcr pooling off)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=False)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 8 and the cfr index to 6
    reader_v2.set_indices(index=8, cfr_index=6, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13266
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2077
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 8 and the cfr index to 6
    reader_v2.set_indices(index=8, cfr_index=6, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13266
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2077
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Loc index = 7

    # Get the reader for the NumPy array (with dcr pooling off)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=False)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 7 and the cfr index to 6
    reader_v2.set_indices(index=7, cfr_index=6, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13720
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2091
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 7 and the cfr index to 6
    reader_v2.set_indices(index=7, cfr_index=6, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13720
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2091
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Loc index = 6

    # Get the reader for the NumPy array (with dcr pooling off)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=False)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 6 and the cfr index to 6
    reader_v2.set_indices(index=6, cfr_index=6, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 14035
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2105
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 6 and the cfr index to 6
    reader_v2.set_indices(index=6, cfr_index=6, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 14035
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 2105
    ), "Unexpected number of unique cfr values."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Loc index = 8, cfr_index = 8

    # Get the reader for the NumPy array (with dcr pooling off)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=False)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 8 and the cfr index to 8
    reader_v2.set_indices(index=8, cfr_index=8, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13266
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 1
    ), "Unexpected number of unique cfr values."
    assert (
        reader_v2.processed_dataframe["cfr"].unique() == -3.05e-05
    ), "Unexpected cfr value."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 8 and the cfr index to 8
    reader_v2.set_indices(index=8, cfr_index=8, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13266
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 1
    ), "Unexpected number of unique cfr values."
    assert (
        reader_v2.processed_dataframe["cfr"].unique() == -3.05e-05
    ), "Unexpected cfr value."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Loc index = 7, cfr_index = 7

    # Get the reader for the NumPy array (with dcr pooling off)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=False)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 7 and the cfr index to 7
    reader_v2.set_indices(index=7, cfr_index=7, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13720
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 1
    ), "Unexpected number of unique cfr values."
    assert (
        reader_v2.processed_dataframe["cfr"].unique() == -3.05e-05
    ), "Unexpected cfr value."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Get the reader for the NumPy array (with dcr pooling on)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=True)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 7 and the cfr index to 7
    reader_v2.set_indices(index=7, cfr_index=7, process=True)

    assert (
        len(reader_v2.processed_dataframe.index) == 13720
    ), "Unexpected total number of entries."
    assert (
        len(reader_v2.processed_dataframe["cfr"].unique()) == 1
    ), "Unexpected number of unique cfr values."
    assert (
        reader_v2.processed_dataframe["cfr"].unique() == -3.05e-05
    ), "Unexpected cfr value."
    assert (
        len(reader_v2.processed_dataframe["tid"].unique()) == 1116
    ), "Unexpected number of unique tid values."

    # Loc index = 6, cfr_index = 9
    # This is NOT allowed

    # Get the reader for the NumPy array (with dcr pooling off)
    npy_file_name_v2 = target_dir / "3d" / "v2.npy"
    reader_v2_class, status_v2 = MinFluxReaderFactory.get_reader(npy_file_name_v2)
    reader_v2 = reader_v2_class(npy_file_name_v2, z_scaling_factor=0.7, pool_dcr=False)

    assert (
        reader_v2_class.__name__ == "MinFluxReaderV2"
    ), "A reader version 2 must be returned for this file."

    # Set the requested localization to 6 and the cfr index to 9
    with pytest.raises(ValueError):
        reader_v2.set_indices(index=6, cfr_index=9, process=True)
