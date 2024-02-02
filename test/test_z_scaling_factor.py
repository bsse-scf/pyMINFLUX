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
#   limitations under the License.
#

import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pyminflux.reader import MinFluxReader


@pytest.fixture(autouse=False)
def extract_multi_format_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    npy_file_name = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    mat_file_name = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    zip_file_name = Path(__file__).parent / "data" / "input_multi_format.zip"
    if not npy_file_name.is_file() or not mat_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_factor_across_readers(extract_multi_format_data_files):

    # z scaling factor
    z_scaling_factor = 0.7

    # Read .npy and .mat files with different scalings
    reader_npy = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    )
    reader_npy_explicit_no_scaling = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy",
        z_scaling_factor=1.0,
    )
    reader_npy_scaled = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy",
        z_scaling_factor=z_scaling_factor,
    )
    reader_mat = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    )
    reader_mat_scaled = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat",
        z_scaling_factor=z_scaling_factor,
    )

    # Check that all files report the same number of rows
    assert len(reader_npy.processed_dataframe.index) == len(
        reader_mat.processed_dataframe.index
    ), "Differing number of dataframe rows."
    assert len(reader_npy.processed_dataframe.index) == len(
        reader_npy_explicit_no_scaling.processed_dataframe.index
    ), "Differing number of dataframe rows."
    assert len(reader_npy_scaled.processed_dataframe.index) == len(
        reader_mat.processed_dataframe.index
    ), "Differing number of dataframe rows."
    assert len(reader_npy_scaled.processed_dataframe.index) == len(
        reader_mat_scaled.processed_dataframe.index
    ), "Differing number of dataframe rows."

    # Check that the scaling is applied correctly
    assert np.allclose(
        reader_npy.processed_dataframe["z"], reader_mat.processed_dataframe["z"]
    ), "z coordinates mismatch."
    assert np.allclose(
        reader_npy.processed_dataframe["z"],
        reader_npy_explicit_no_scaling.processed_dataframe["z"],
    ), "z coordinates mismatch."
    assert np.allclose(
        reader_npy_scaled.processed_dataframe["z"],
        reader_mat_scaled.processed_dataframe["z"],
    ), "z coordinates mismatch."
    assert np.allclose(
        z_scaling_factor * reader_npy.processed_dataframe["z"],
        reader_npy_scaled.processed_dataframe["z"],
    ), "Unexpected scaling."
    assert np.allclose(
        z_scaling_factor * reader_mat.processed_dataframe["z"],
        reader_mat_scaled.processed_dataframe["z"],
    ), "Unexpected scaling."
    assert np.allclose(
        z_scaling_factor * reader_npy.processed_dataframe["z"],
        reader_mat_scaled.processed_dataframe["z"],
    ), "Unexpected scaling."
    assert np.allclose(
        z_scaling_factor * reader_mat.processed_dataframe["z"],
        reader_npy_scaled.processed_dataframe["z"],
    ), "Unexpected scaling."
