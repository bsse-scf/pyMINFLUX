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

import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.reader import MinFluxReader


@pytest.fixture(autouse=False)
def extract_tracking_archives(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    npy_file_names = [
        Path(__file__).parent / "data" / "2D_Tracking.npy",
        # Path(__file__).parent / "data" / "3d_Tracking.npy",
    ]

    # Make sure to extract the test data if it is not already there
    need_to_extract = False
    for npy_file_name in npy_file_names:
        if not npy_file_name.is_file():
            need_to_extract = True
            break

    if need_to_extract:
        archive_filename = Path(__file__).parent / "data" / "2D_Tracking.npy.zip"
        with zipfile.ZipFile(archive_filename, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_2d_tracking(extract_tracking_archives):
    #
    # 2D_Tracking.npy
    #
    # Using NumPy

    # Load data
    tracking_2d = np.load(Path(__file__).parent / "data" / "2D_Tracking.npy")
    assert tracking_2d is not None, "Could not load file."

    # Check structure
    assert len(tracking_2d.dtype.names) == 9, "Unexpected number of features."
    assert np.all(
        tracking_2d.dtype.names
        == ("itr", "sqi", "gri", "tim", "tid", "vld", "act", "dos", "sky")
    ), "Unexpected feature names."
    assert np.all(
        tracking_2d["itr"].dtype.names
        == (
            "itr",
            "tic",
            "loc",
            "eco",
            "ecc",
            "efo",
            "efc",
            "sta",
            "cfr",
            "dcr",
            "ext",
            "gvy",
            "gvx",
            "eoy",
            "eox",
            "dmz",
            "lcy",
            "lcx",
            "lcz",
            "fbg",
            "lnc",
        )
    ), "Unexpected 'itr' feature names."
    assert tracking_2d["itr"].shape[1] == 4, "Unexpected number of 'itr' localizations."

    # Check data
    efo = tracking_2d["itr"]["efo"][:, 3]
    assert len(efo) == 38105, "Unexpected number of 'efo' measurements."
    assert (
        pytest.approx(efo.min(), 1e-4) == 60060.06006006006
    ), "Unexpected min value of 'efo'."
    assert (
        pytest.approx(efo.max(), 1e-4) == 880880.8808808809
    ), "Unexpected max value of 'efo'."

    cfr = tracking_2d["itr"]["cfr"][:, 3]
    assert len(cfr) == 38105, "Unexpected number of 'cfr' measurements."
    assert (
        pytest.approx(cfr.min(), 1e-4) == -3.0517578125e-05
    ), "Unexpected min value of 'cfr'."
    assert (
        pytest.approx(cfr.max(), 1e-4) == -3.0517578125e-05
    ), "Unexpected max value of 'cfr'."

    #
    # 2D_Tracking.npy
    #
    # Using MinFluxReader

    # Load data
    tracking_2d = MinFluxReader(Path(__file__).parent / "data" / "2D_Tracking.npy")
    assert tracking_2d.num_valid_entries != 0, "Could not load file."
    assert tracking_2d.num_valid_entries == 38105, "Unexpected number of valid entries."

    # Check data
    efo = tracking_2d.processed_dataframe["efo"]
    assert efo.min() == 60060.06006006006, "Unexpected min value of 'efo'."
    assert efo.max() == 880880.8808808809, "Unexpected max value of 'efo'."

    cfr = tracking_2d.processed_dataframe["cfr"]
    assert cfr.min() == -3.0517578125e-05, "Unexpected min value of 'cfr'."
    assert cfr.max() == -3.0517578125e-05, "Unexpected max value of 'cfr'."
