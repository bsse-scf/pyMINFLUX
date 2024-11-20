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

from pyminflux.reader import MinFluxReader, MinFluxReaderFactory


@pytest.fixture(autouse=False)
def extract_multi_format_geometry_data_files(tmpdir):
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

    npy_3d_file_name = Path(__file__).parent / "data" / "3D_ValidOnly.npy"
    zip_3d_file_name = Path(__file__).parent / "data" / "3D_ValidOnly.npy.zip"
    if not npy_3d_file_name.is_file():
        with zipfile.ZipFile(zip_3d_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_compare_readers(extract_multi_format_geometry_data_files):
    # Read both formats
    reader_npy = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    )
    reader_mat = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    )

    # Compare the dimensions of the read dataframes
    assert (
        reader_npy.processed_dataframe.shape == reader_mat.processed_dataframe.shape
    ), "Dimensions mismatch."
    # Compare the read dataframes
    assert np.allclose(
        reader_npy.processed_dataframe.to_numpy(),
        reader_mat.processed_dataframe.to_numpy(),
        equal_nan=True,
    ), "Mismatch in read values."


def test_access(extract_multi_format_geometry_data_files):
    # Read a 3D dataset (and set it as tracking)
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "3D_ValidOnly.npy",
        is_tracking=True,
        dwell_time=0.05,
        pool_dcr=True,
        z_scaling_factor=0.7,
    )

    # Before accessing the processed_dataframe, most values are set, with the
    # exception if `is_last_valid` that returns None
    assert reader.is_3d is True, "The 3D information is extracted at load/scan."
    assert (
        reader.is_aggregated is False
    ), "Whether the data is aggregated is extracted at load/scan."
    assert (
        reader.is_last_valid is None
    ), "The last valid information is extracted when processing."
    assert (
        reader.is_tracking is True
    ), "The tracking flag is passed as a parameter to the constructor."
    assert np.all(
        reader.valid_cfr
        == [False, False, True, False, False, False, True, False, False, False]
    ), "The valid CFR iterations flag is extracted at load/scan."
    assert np.all(
        reader.relocalizations
        == [False, False, False, False, False, False, True, True, True, True]
    ), "The relocalized iterations flag is extracted at load/scan."
    assert (
        reader.z_scaling_factor == 0.7
    ), "The z scaling factor is passed as a parameter to the constructor."
    assert (
        reader.dwell_time == 0.05
    ), "The dwell time is passed as a parameter to the constructor."
    assert (
        reader.is_pool_dcr is True
    ), "The pool DCR flag is passed as a parameter to the constructor."

    # Now access the raw dataframe, this will not change the properties from above.
    # The property `is_last_valid` is still None
    df_raw = reader.raw_data_dataframe
    assert df_raw is not None, "The raw dataframe is generated at access."

    assert reader.is_3d is True, "The 3D information is extracted at load/scan."
    assert (
        reader.is_aggregated is False
    ), "Whether the data is aggregated is extracted at load/scan."
    assert (
        reader.is_last_valid is None
    ), "The last valid information is extracted when processing."
    assert (
        reader.is_tracking is True
    ), "The tracking flag is passed as a parameter to the constructor."
    assert np.all(
        reader.valid_cfr
        == [False, False, True, False, False, False, True, False, False, False]
    ), "The valid CFR iterations flag is extracted at load/scan."
    assert np.all(
        reader.relocalizations
        == [False, False, False, False, False, False, True, True, True, True]
    ), "The relocalized iterations flag is extracted at load/scan."
    assert (
        reader.z_scaling_factor == 0.7
    ), "The z scaling factor is passed as a parameter to the constructor."
    assert (
        reader.dwell_time == 0.05
    ), "The dwell time is passed as a parameter to the constructor."
    assert (
        reader.is_pool_dcr is True
    ), "The pool DCR flag is passed as a parameter to the constructor."

    # Now access the processed_dataframe, that will force its creation and the update
    # of `is_last_valid`. All other properties do not change.
    df = reader.processed_dataframe
    assert df is not None, "The dataframe is generated at access."

    assert reader.is_3d is True, "The 3D information is extracted at load/scan."
    assert (
        reader.is_aggregated is False
    ), "Whether the data is aggregated is extracted at load/scan."
    assert (
        reader.is_last_valid is True
    ), "The last valid information is extracted when processing."
    assert (
        reader.is_tracking is True
    ), "The tracking flag is passed as a parameter to the constructor."
    assert np.all(
        reader.valid_cfr
        == [False, False, True, False, False, False, True, False, False, False]
    ), "The valid CFR iterations flag is extracted at load/scan."
    assert np.all(
        reader.relocalizations
        == [False, False, False, False, False, False, True, True, True, True]
    ), "The relocalized iterations flag is extracted at load/scan."
    assert (
        reader.z_scaling_factor == 0.7
    ), "The z scaling factor is passed as a parameter to the constructor."
    assert (
        reader.dwell_time == 0.05
    ), "The dwell time is passed as a parameter to the constructor."
    assert (
        reader.is_pool_dcr is True
    ), "The pool DCR flag is passed as a parameter to the constructor."

    # Now change something - the `process` flag in the methods below allow to postpone the
    # processing of the NumPy array into the dataframe, but only if dataframe has not been
    # created yet.
    reader.set_tracking(False, process=False)
    assert reader.is_tracking is False, "The tracking flag is changed immediately."

    reader.set_indices(4, 4, process=False)
    assert (
        reader.is_last_valid is False
    ), "The selected iteration is no longer the last valid."

    reader.set_dwell_time(1.0, process=False)
    assert reader.dwell_time == 1.0, "The dwell time is changed immediately."

    dcr_before = reader.processed_dataframe["dcr"].to_numpy()
    reader.set_pool_dcr(False, process=False)
    assert reader.is_pool_dcr is False, "The is_pool_dcr flag is changed immediately."


def test_reader_factory(extract_multi_format_geometry_data_files):
    # Get the reader for the NumPy array
    npy_file_name = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    reader, status = MinFluxReaderFactory.get_reader(npy_file_name)

    assert reader is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader.__name__ == "MinFluxReader"
    ), "A reader version 1 must be returned for this file."

    # Get the reader for the MAT array
    mat_file_name = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    reader, status = MinFluxReaderFactory.get_reader(mat_file_name)

    assert reader is not None, "A reader must be returned for this file."
    assert status == "", "No error message expected."
    assert (
        reader.__name__ == "MinFluxReader"
    ), "A reader version 1 must be returned for this file."
