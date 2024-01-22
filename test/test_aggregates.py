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
def extract_aggregates_archives(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    npy_file_names = [
        Path(__file__).parent / "data" / "2D_aggregates.npy",
        Path(__file__).parent / "data" / "3D_aggregates.npy",
    ]

    # Make sure to extract the test data if it is not already there
    need_to_extract = False
    for npy_file_name in npy_file_names:
        if not npy_file_name.is_file():
            need_to_extract = True
            break

    if need_to_extract:
        archive_filename = Path(__file__).parent / "data" / "aggregates.npy.zip"
        with zipfile.ZipFile(archive_filename, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_aggregates(extract_aggregates_archives):
    #
    # 2D_aggregates.npy
    #

    # Load data
    aggr_2d = np.load(Path(__file__).parent / "data" / "2D_aggregates.npy")
    assert aggr_2d is not None, "Could not load file."

    # Check structure
    assert aggr_2d["itr"].shape[1] == 1, "Unexpected number of 'itr' localizations."
    assert len(aggr_2d) == 7583, "Unexpected number of traces."

    #
    # 3D_aggregates.npy
    #

    # Load data
    aggr_3d = np.load(Path(__file__).parent / "data" / "3D_aggregates.npy")
    assert aggr_3d is not None, "Could not load file."

    # Check structure
    assert aggr_3d["itr"].shape[1] == 1, "Unexpected number of 'itr' localizations."
    assert len(aggr_3d) == 12219, "Unexpected number of traces."
