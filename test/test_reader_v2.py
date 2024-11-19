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

import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.reader import MinFluxReader, MinFluxReaderV2


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
    jsn_file_name = target_dir / "241107-115322_minflux.json"
    npy_file_name = target_dir / "241107-115322_minflux.npy"
    mat_file_name = target_dir / "241107-115322_minflux.mat"
    zip_file_name = data_dir / "reader_v2.zip"
    if (
        not npy_file_name.is_file()
        or not mat_file_name.is_file()
        or not jsn_file_name.is_file()
    ):
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
    assert npy_reader._data_full_df.equals(
        mat_reader._data_full_df
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
    assert npy_reader._data_full_df.equals(
        json_reader._data_full_df
    ), "NumPy and json dataframe are different."

    #
    # Test processor
    #
